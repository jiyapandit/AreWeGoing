import { AlertTriangle, CheckCircle2, Layers } from "lucide-react";
import { useState } from "react";
import { FluidDropdown } from "@/components/ui/fluid-dropdown";

export default function FluidDropdownDemo() {
  const [voteValue, setVoteValue] = useState("APPROVE");
  const options = [
    { id: "ALL", label: "All", icon: Layers, color: "#A06CD5" },
    { id: "APPROVE", label: "Approve", icon: CheckCircle2, color: "#34D399" },
    { id: "CHANGES", label: "Request Changes", icon: AlertTriangle, color: "#F59E0B" },
  ];

  return <FluidDropdown options={options} value={voteValue} onChange={setVoteValue} />;
}
