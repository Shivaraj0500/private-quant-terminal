import { useQuery } from "@tanstack/react-query";

import { getUpstoxStatus } from "../../../api/upstox";

export function useUpstoxStatus() {
  return useQuery({
    queryKey: ["upstox", "status"],
    queryFn: getUpstoxStatus,
    refetchInterval: 30000,
  });
}
