import { useMutation, useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  checkForAppUpdate,
  getAppVersion,
  installAppUpdate,
} from "@/lib/updater";

export function AppUpdateCard() {
  const { data: version } = useQuery({
    queryKey: ["app-version"],
    queryFn: getAppVersion,
  });

  const {
    data: update,
    isFetching,
    refetch,
  } = useQuery({
    queryKey: ["app-update"],
    queryFn: checkForAppUpdate,
    enabled: version != null,
    retry: false,
  });

  const install = useMutation({
    mutationFn: installAppUpdate,
  });

  if (version == null) {
    return null;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Application</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3 text-xs">
        <p className="text-muted-foreground">
          Installed version:{" "}
          <span className="font-mono text-foreground">{version}</span>
        </p>

        {update ? (
          <div className="space-y-2 rounded-md border border-border p-3">
            <p className="text-foreground">
              Update available:{" "}
              <span className="font-mono">{update.nextVersion}</span>
            </p>
            {update.notes && (
              <p className="whitespace-pre-wrap text-muted-foreground">
                {update.notes}
              </p>
            )}
            <Button
              size="sm"
              disabled={install.isPending}
              onClick={() => install.mutate()}
            >
              {install.isPending ? "Installing…" : "Install update"}
            </Button>
          </div>
        ) : (
          <p className="text-muted-foreground">You are on the latest release.</p>
        )}

        <Button
          size="sm"
          variant="outline"
          disabled={isFetching || install.isPending}
          onClick={() => refetch()}
        >
          {isFetching ? "Checking…" : "Check for updates"}
        </Button>
      </CardContent>
    </Card>
  );
}
