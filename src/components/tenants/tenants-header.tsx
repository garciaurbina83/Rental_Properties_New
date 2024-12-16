import { Button } from "@/components/ui/button"
import { PlusCircle, Grid, List } from "lucide-react"

interface TenantsHeaderProps {
  onCreateClick: () => void
  viewMode: "grid" | "table"
  onViewModeChange: (mode: "grid" | "table") => void
}

export function TenantsHeader({
  onCreateClick,
  viewMode,
  onViewModeChange,
}: TenantsHeaderProps) {
  return (
    <div className="flex items-center justify-between space-y-2">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Tenants</h2>
        <p className="text-muted-foreground">
          Here&apos;s a list of all your tenants
        </p>
      </div>
      <div className="flex items-center space-x-2">
        <Button
          variant="outline"
          size="icon"
          onClick={() => onViewModeChange("grid")}
          className={viewMode === "grid" ? "bg-muted" : ""}
        >
          <Grid className="h-4 w-4" />
        </Button>
        <Button
          variant="outline"
          size="icon"
          onClick={() => onViewModeChange("table")}
          className={viewMode === "table" ? "bg-muted" : ""}
        >
          <List className="h-4 w-4" />
        </Button>
        <Button onClick={onCreateClick}>
          <PlusCircle className="mr-2 h-4 w-4" />
          Add Tenant
        </Button>
      </div>
    </div>
  )
}
