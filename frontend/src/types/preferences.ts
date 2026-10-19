export interface UserPreferences {
  email_notifications_enabled: boolean;
  in_app_notifications_enabled: boolean;
  ai_suggestions_enabled: boolean;
  created_at?: string | null;
  updated_at?: string | null;
}

export type PreferencesUpdate = Partial<
  Pick<
    UserPreferences,
    | "email_notifications_enabled"
    | "in_app_notifications_enabled"
    | "ai_suggestions_enabled"
  >
>;

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

export interface ChangePasswordResponse {
  message: string;
}
