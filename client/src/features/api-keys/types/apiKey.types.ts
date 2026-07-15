export interface ApiKey {
  id: string;
  name: string;
  key_prefix: string;
  last_used_at: string | null;
  revoked_at: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface ApiKeyCreatedResponse {
  id: string;
  name: string;
  secret: string;
  key_prefix: string;
  created_at: string | null;
}
