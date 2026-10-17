export interface User {
  id: string;
  email?: string;
  display_name: string;
  avatar_url?: string;
  role: string;
}

export interface Place {
  id: string;
  name: string;
  category: string;
  address: string;
  city?: string;
  latitude: number;
  longitude: number;
  phone?: string;
  website?: string;
  price_level: number;
  estimated_price_eur?: number;
  is_halal?: boolean;
  has_terrace?: boolean;
  has_parking?: boolean;
  is_wheelchair_accessible?: boolean;
  photos: string[];
}

export interface Participant {
  id: string;
  meeting_id: string;
  name: string;
  is_guest: boolean;
  departure_label?: string;
  departure_lat?: number;
  departure_lon?: number;
  hide_exact_location: boolean;
  transport_mode: string;
  max_travel_time_minutes: number;
  max_budget?: number;
  dietary_constraints: string[];
  accessibility_needs: string[];
  has_submitted: boolean;
}

export interface Candidate {
  id: string;
  meeting_id: string;
  place: Place;
  total_score: number;
  is_eligible: boolean;
  disqualification_reason?: string;
  max_duration_seconds: number;
  mean_duration_seconds: number;
  duration_variance: number;
  in_shortlist: boolean;
  routes_summary: any[];
  explanation?: string;
  votes_count: number;
}

export interface Meeting {
  id: string;
  title: string;
  description?: string;
  category: string;
  status: string;
  organizer_id: string;
  proposed_date?: string;
  duration_minutes: number;
  max_budget_per_person?: number;
  optimization_strategy: string;
  confirmed_place_id?: string;
  confirmed_place?: Place;
  mandatory_criteria: Record<string, any>;
  optional_preferences: Record<string, any>;
  participants: Participant[];
  created_at: string;
}
