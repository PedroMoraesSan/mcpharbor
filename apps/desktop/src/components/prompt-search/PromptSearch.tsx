import { Search } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Input } from "@/components/ui/input";
import { useAppStore } from "@/stores/app.store";

export function PromptSearch() {
  const { searchQuery, setSearchQuery } = useAppStore();
  const navigate = useNavigate();

  return (
    <div className="relative w-full max-w-md">
      <Search className="absolute left-0 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
      <Input
        placeholder="Search MCPs..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter") navigate("/catalog");
        }}
        className="pl-7"
      />
    </div>
  );
}
