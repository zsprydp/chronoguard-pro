// Shared types and utilities for ChronoGuard Pro

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  practice_name: string;
  phone?: string;
  created_at: Date;
  updated_at: Date;
}

export interface Practice {
  id: string;
  name: string;
  user_id: string;
  created_at: Date;
  updated_at: Date;
}

export interface Appointment {
  id: string;
  patient_id: string;
  provider_id: string;
  practice_id: string;
  scheduled_time: Date;
  duration_minutes: number;
  status: AppointmentStatus;
  no_show_probability?: number;
  created_at: Date;
  updated_at: Date;
}

export enum AppointmentStatus {
  SCHEDULED = 'scheduled',
  CONFIRMED = 'confirmed',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled',
  NO_SHOW = 'no_show'
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

// Utility functions
export const formatDate = (date: Date): string => {
  return date.toISOString().split('T')[0];
};

export const formatDateTime = (date: Date): string => {
  return date.toISOString().replace('T', ' ').split('.')[0];
};

export const calculateNoShowRisk = (probability: number): 'low' | 'medium' | 'high' => {
  if (probability < 0.3) return 'low';
  if (probability < 0.7) return 'medium';
  return 'high';
};
