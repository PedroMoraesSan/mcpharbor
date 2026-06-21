use std::collections::HashMap;
use std::fs::{self, OpenOptions};
use std::io::Write;
use std::path::{Path, PathBuf};
use std::sync::Mutex;

use tauri::{Manager, RunEvent};
use tauri_plugin_shell::ShellExt;
use tauri_plugin_shell::process::{CommandChild, CommandEvent};

struct SidecarState {
    child: Mutex<Option<CommandChild>>,
}

fn mcpharbour_dir() -> PathBuf {
    std::env::var("HOME")
        .map(PathBuf::from)
        .unwrap_or_default()
        .join(".mcpharbour")
}

/// Ensure user data directories exist. Config file is created by the Python sidecar.
fn ensure_user_dirs() -> PathBuf {
    let dir = mcpharbour_dir();
    let _ = fs::create_dir_all(dir.join("logs"));
    dir.join(".env")
}

fn parse_env_file(path: &Path) -> HashMap<String, String> {
    let mut values = HashMap::new();
    let Ok(content) = fs::read_to_string(path) else {
        return values;
    };

    for line in content.lines() {
        let line = line.trim();
        if line.is_empty() || line.starts_with('#') {
            continue;
        }
        let Some((key, value)) = line.split_once('=') else {
            continue;
        };
        let trimmed = value.trim().trim_matches('"').trim_matches('\'');
        values.insert(key.trim().to_string(), trimmed.to_string());
    }

    values
}

fn augmented_path(current: &str) -> String {
    let extra = [
        "/Applications/Docker.app/Contents/Resources/bin",
        "/usr/local/bin",
        "/opt/homebrew/bin",
    ];
    let mut parts: Vec<String> = extra
        .iter()
        .filter(|path| Path::new(path).is_dir())
        .map(|path| (*path).to_string())
        .collect();

    for segment in current.split(':') {
        if segment.is_empty() {
            continue;
        }
        if !parts.iter().any(|existing| existing == segment) {
            parts.push(segment.to_string());
        }
    }

    parts.join(":")
}

fn append_sidecar_log(log_path: &Path, message: &str) {
    if let Ok(mut file) = OpenOptions::new()
        .create(true)
        .append(true)
        .open(log_path)
    {
        let _ = writeln!(file, "{message}");
    }
}

fn monitor_sidecar(mut rx: tauri::async_runtime::Receiver<CommandEvent>, log_path: PathBuf) {
    tauri::async_runtime::spawn(async move {
        while let Some(event) = rx.recv().await {
            match event {
                CommandEvent::Stdout(line) => {
                    let text = String::from_utf8_lossy(&line);
                    append_sidecar_log(&log_path, &format!("[stdout] {text}"));
                }
                CommandEvent::Stderr(line) => {
                    let text = String::from_utf8_lossy(&line);
                    append_sidecar_log(&log_path, &format!("[stderr] {text}"));
                }
                CommandEvent::Terminated(payload) => {
                    append_sidecar_log(
                        &log_path,
                        &format!(
                            "[terminated] code={:?} signal={:?}",
                            payload.code, payload.signal
                        ),
                    );
                }
                CommandEvent::Error(err) => {
                    append_sidecar_log(&log_path, &format!("[error] {err}"));
                }
                _ => {}
            }
        }
    });
}

fn free_port(port: u16, log_path: &Path) {
    #[cfg(unix)]
    {
        use std::process::Command;
        let Ok(output) = Command::new("lsof")
            .args(["-ti", &format!("tcp:{port}")])
            .output()
        else {
            return;
        };

        let pids = String::from_utf8_lossy(&output.stdout);
        for pid in pids.split_whitespace() {
            append_sidecar_log(
                log_path,
                &format!("Releasing stale listener on port {port}: pid={pid}"),
            );
            let _ = Command::new("kill").args(["-9", pid]).status();
        }
    }
}

fn spawn_api_sidecar(app: &tauri::App) {
    let env_path = ensure_user_dirs();
    let log_path = mcpharbour_dir().join("logs").join("sidecar.log");
    free_port(8741, &log_path);
    append_sidecar_log(&log_path, "Spawning mcpharbour-api sidecar");

    let mut env_vars = parse_env_file(&env_path);
    let base_path = env_vars
        .remove("PATH")
        .or_else(|| std::env::var("PATH").ok())
        .unwrap_or_default();
    env_vars.insert("PATH".to_string(), augmented_path(&base_path));

    let sidecar = match app.shell().sidecar("mcpharbour-api") {
        Ok(sidecar) => sidecar,
        Err(err) => {
            append_sidecar_log(&log_path, &format!("Failed to create sidecar command: {err}"));
            eprintln!("Failed to create API sidecar command: {err}");
            return;
        }
    };

    let mut sidecar = sidecar.args(["--host", "127.0.0.1", "--port", "8741"]);
    for (key, value) in env_vars {
        sidecar = sidecar.env(key, value);
    }
    sidecar = sidecar.env("MCPHARBOR_ENV", "production");

    match sidecar.spawn() {
        Ok((rx, child)) => {
            monitor_sidecar(rx, log_path);
            app.manage(SidecarState {
                child: Mutex::new(Some(child)),
            });
        }
        Err(err) => {
            append_sidecar_log(&log_path, &format!("Failed to spawn sidecar: {err}"));
            eprintln!("Failed to spawn API sidecar: {err}");
        }
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_http::init())
        .plugin(tauri_plugin_updater::Builder::new().build())
        .plugin(tauri_plugin_process::init())
        .setup(|app| {
            spawn_api_sidecar(app);
            Ok(())
        })
        .build(tauri::generate_context!())
        .expect("error while building tauri application")
        .run(|app, event| {
            if let RunEvent::Exit = event {
                if let Some(state) = app.try_state::<SidecarState>() {
                    if let Ok(mut guard) = state.child.lock() {
                        if let Some(child) = guard.take() {
                            let _ = child.kill();
                        }
                    }
                }
            }
        });
}
