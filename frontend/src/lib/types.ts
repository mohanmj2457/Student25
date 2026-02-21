import { z } from 'zod';

export const SubjectSchema = z.object({
  id: z.string(),
  name: z.string().min(1, 'Subject name is required.'),
  credits: z.coerce.number().min(0.5, 'Credits must be at least 0.5.').max(10, 'Credits cannot exceed 10.'),
  marks: z.coerce.number().min(0, 'Marks must be non-negative.').max(100, 'Marks cannot exceed 100.'),
  target: z.coerce.number().min(0, 'Target must be non-negative.').max(100, 'Target cannot exceed 100.'),
});

export const GpaFormSchema = z.object({
  subjects: z.array(SubjectSchema).min(1, 'Please add at least one subject.'),
});

export type Subject = z.infer<typeof SubjectSchema>;
export type GpaFormData = z.infer<typeof GpaFormSchema>;

export type AnalysisResult = {
  currentGpa: number;
  targetGpa: number;
  subjects: Array<Subject & { requiredImprovement: number }>;
  prioritizedSubjects: string[];
};
