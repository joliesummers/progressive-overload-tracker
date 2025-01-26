export type MuscleActivationLevel = 'PRIMARY' | 'SECONDARY' | 'TERTIARY';

export interface MuscleActivation {
  muscle_name: string;
  activation_level: MuscleActivationLevel;
  estimated_volume: number;
}

export interface Exercise {
  exercise_name: string;
  muscle_activations: MuscleActivation[];
  movement_pattern: string;
  equipment_needed: string[];
  notes?: string;
}

export interface WorkoutSet {
  exercise: Exercise;
  sets: number;
  reps: number;
  weight?: number;
  rpe?: number;
  tempo?: string;
  notes?: string;
}

export interface WorkoutSession {
  id: string;
  date: Date;
  sets: WorkoutSet[];
  sentiment_score?: number;
  sentiment_analysis?: string;
  notes?: string;
}

export interface MuscleTrackingStatus {
  muscle_name: string;
  last_trained: string;
  days_since_last_trained: number;
}

export interface MuscleVolumeData {
  muscle_name: string;
  total_volume: number;
  date: string;
}

export interface VolumeDataPoint {
  date: string;
  volume: number;
}

export interface VolumeProgressionResponse {
  [muscleName: string]: VolumeDataPoint[];
}

export interface VolumeProgressionData {
  muscle_name: string;
  date: string;
  total_volume: number;
}
