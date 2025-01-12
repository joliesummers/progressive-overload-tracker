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
  last_workout: string;
  recovery_status: 'Recovered' | 'Recovering' | 'Fatigued';
  volume_trend: number;
  sets_last_week: number;
}
