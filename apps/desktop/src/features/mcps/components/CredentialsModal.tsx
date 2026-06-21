import { useEffect, useState } from "react";
import { Eye, EyeOff, KeyRound, Loader2, ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

export type CredentialFieldDef = {
  key: string;
  label: string;
  required: boolean;
};

type CredentialsModalProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  mcpName: string;
  fields: CredentialFieldDef[];
  onSave: (values: Record<string, string>) => void;
  isSaving?: boolean;
  isUpdate?: boolean;
};

function CredentialInput({
  field,
  value,
  onChange,
}: {
  field: CredentialFieldDef;
  value: string;
  onChange: (value: string) => void;
}) {
  const [visible, setVisible] = useState(false);

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between gap-2">
        <label
          htmlFor={`cred-${field.key}`}
          className="text-sm font-medium text-foreground"
        >
          {field.label}
          {field.required ? (
            <span className="ml-1 text-destructive" aria-hidden>
              *
            </span>
          ) : null}
        </label>
        <span className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground/70">
          {field.key}
        </span>
      </div>
      <div className="relative">
        <Input
          id={`cred-${field.key}`}
          type={visible ? "text" : "password"}
          placeholder={`Enter ${field.label.toLowerCase()}`}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="rounded-lg border border-border/60 bg-secondary/20 px-3 pr-10"
          autoComplete="off"
        />
        <button
          type="button"
          onClick={() => setVisible((v) => !v)}
          className="absolute right-2 top-1/2 -translate-y-1/2 rounded-md p-1 text-muted-foreground transition-colors hover:text-foreground"
          aria-label={visible ? "Hide value" : "Show value"}
        >
          {visible ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
        </button>
      </div>
    </div>
  );
}

export function CredentialsModal({
  open,
  onOpenChange,
  mcpName,
  fields,
  onSave,
  isSaving = false,
  isUpdate = false,
}: CredentialsModalProps) {
  const [values, setValues] = useState<Record<string, string>>({});

  useEffect(() => {
    if (open) setValues({});
  }, [open]);

  const hasAllRequired = fields
    .filter((f) => f.required)
    .every((f) => values[f.key]?.trim());

  const handleSave = () => {
    if (!hasAllRequired) return;
    onSave(values);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="console-floating-surface gap-0 overflow-hidden rounded-2xl border-border/60 p-0 sm:max-w-md">
        <div className="border-b border-border/50 bg-primary/5 px-6 py-5">
          <DialogHeader className="space-y-3 text-left">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-primary/20 bg-primary/10">
              <KeyRound className="h-5 w-5 text-primary" />
            </div>
            <div>
              <DialogTitle className="font-display text-xl uppercase tracking-wider">
                {isUpdate ? "Update credentials" : "Add credentials"}
              </DialogTitle>
              <DialogDescription className="mt-1.5 text-sm">
                {isUpdate
                  ? `Replace the secrets stored for ${mcpName}. Values are never shown after saving.`
                  : `Configure the secrets required to run ${mcpName}.`}
              </DialogDescription>
            </div>
          </DialogHeader>
        </div>

        <div className="space-y-5 px-6 py-5">
          {fields.map((field) => (
            <CredentialInput
              key={field.key}
              field={field}
              value={values[field.key] ?? ""}
              onChange={(v) => setValues((prev) => ({ ...prev, [field.key]: v }))}
            />
          ))}

          <div className="flex items-start gap-2.5 rounded-xl border border-border/50 bg-secondary/15 px-3 py-3">
            <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
            <p className="text-xs leading-relaxed text-muted-foreground">
              Secrets are encrypted and stored in your OS keychain. They are injected into the
              container at runtime and never written to disk in plain text.
            </p>
          </div>
        </div>

        <DialogFooter className="border-t border-border/50 bg-secondary/10 px-6 py-4 sm:justify-between">
          <Button
            type="button"
            variant="ghost"
            onClick={() => onOpenChange(false)}
            disabled={isSaving}
          >
            Cancel
          </Button>
          <Button
            type="button"
            onClick={handleSave}
            disabled={!hasAllRequired || isSaving}
            className="min-w-[140px]"
          >
            {isSaving ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Saving…
              </>
            ) : (
              "Save to keychain"
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
