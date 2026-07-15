import { Mail } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export function GuestsCard({ guests }: { guests: string[] }) {
  if (guests.length === 0) return null;

  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="text-base flex items-center gap-2">
          <Mail className="h-4 w-4" />
          Guests
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-wrap gap-2">
          {guests.map((email) => (
            <Badge key={email} variant="secondary">
              {email}
            </Badge>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
