"use client";

import { useState } from 'react';
import { useForm, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { GpaFormData, GpaFormSchema, AnalysisResult } from '@/lib/types';
import { useToast } from '@/hooks/use-toast';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Loader2, PlusCircle, Trash2, Target, TrendingUp, ListChecks, BarChart } from 'lucide-react';
import { Bar, BarChart as RechartsBarChart, ResponsiveContainer, XAxis, YAxis, Tooltip, Legend } from 'recharts';
import { ChartContainer, ChartTooltipContent, type ChartConfig } from "@/components/ui/chart"

const chartConfig = {
  current: {
    label: "Current Marks",
    color: "hsl(var(--secondary))",
  },
  target: {
    label: "Target Marks",
    color: "hsl(var(--primary))",
  },
} satisfies ChartConfig

export function GPADashboard() {
  const { toast } = useToast();
  const [isPending, setIsPending] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);

  const form = useForm<GpaFormData>({
    resolver: zodResolver(GpaFormSchema),
    defaultValues: {
      subjects: [
        { id: crypto.randomUUID(), name: 'Data Structures', credits: 3, marks: 85, target: 92 },
        { id: crypto.randomUUID(), name: 'Algorithms', credits: 3, marks: 78, target: 90 },
        { id: crypto.randomUUID(), name: 'Database Systems', credits: 4, marks: 82, target: 88 },
      ],
    },
  });

  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: 'subjects',
  });

  const onSubmit = async (data: GpaFormData) => {
    setIsPending(true);
    setAnalysisResult(null);

    try {
      const response = await fetch('http://localhost:8000/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ subjects: data.subjects }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const result: AnalysisResult = await response.json();
      
      setAnalysisResult(result);
      toast({
        title: 'Analysis Complete',
        description: 'Your GPA analysis has been calculated.',
      });
    } catch (error) {
      console.error("Failed to fetch GPA analysis:", error);
      toast({
        variant: 'destructive',
        title: 'Analysis Failed',
        description: 'Could not connect to the analysis engine. Please try again.',
      });
    } finally {
      setIsPending(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
      <div className="lg:col-span-2">
        <Card className="glass-card">
          <CardHeader>
            <CardTitle className="font-headline text-2xl flex items-center gap-2">
              <BarChart className="text-primary" />
              Subject & Grade Input
            </CardTitle>
            <CardDescription>Add your subjects, credits, and grades to get started.</CardDescription>
          </CardHeader>
          <CardContent>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                <div className="space-y-4 max-h-[400px] overflow-y-auto pr-2">
                  {fields.map((field, index) => (
                    <div key={field.id} className="p-4 border rounded-lg bg-background/50 relative">
                       <FormLabel className="text-base font-semibold">{`Subject ${index + 1}`}</FormLabel>
                       <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
                        <FormField
                          control={form.control}
                          name={`subjects.${index}.name`}
                          render={({ field }) => (
                            <FormItem className="md:col-span-2">
                              <FormControl><Input placeholder="Subject Name" {...field} /></FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                        <FormField
                          control={form.control}
                          name={`subjects.${index}.credits`}
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel className="text-xs">Credits</FormLabel>
                              <FormControl><Input type="number" placeholder="e.g. 3" {...field} /></FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                         <FormField
                          control={form.control}
                          name={`subjects.${index}.marks`}
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel className="text-xs">Current Marks (%)</FormLabel>
                              <FormControl><Input type="number" placeholder="e.g. 85" {...field} /></FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                        <FormField
                          control={form.control}
                          name={`subjects.${index}.target`}
                          render={({ field }) => (
                            <FormItem className="md:col-span-2">
                              <FormLabel className="text-xs">Target Marks (%)</FormLabel>
                              <FormControl><Input type="number" placeholder="e.g. 92" {...field} /></FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                      </div>
                      <Button type="button" variant="ghost" size="icon" className="absolute top-2 right-2 text-muted-foreground hover:text-destructive" onClick={() => remove(index)}>
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                </div>
                {form.formState.errors.subjects?.root && <p className="text-sm font-medium text-destructive">{form.formState.errors.subjects.root.message}</p>}
                
                <Button type="button" variant="outline" className="w-full" onClick={() => append({ id: crypto.randomUUID(), name: '', credits: 3, marks: 0, target: 0 })}>
                  <PlusCircle className="mr-2 h-4 w-4" /> Add Subject
                </Button>

                <Button type="submit" disabled={isPending} className="w-full font-bold text-lg py-6 bg-primary text-primary-foreground hover:bg-primary/90 transition-all duration-300 hover:glow-primary">
                  {isPending ? <Loader2 className="mr-2 h-6 w-6 animate-spin" /> : 'Analyze My GPA'}
                </Button>
              </form>
            </Form>
          </CardContent>
        </Card>
      </div>
      
      <div className="lg:col-span-3">
        {isPending && (
           <Card className="glass-card h-full flex items-center justify-center">
             <div className="text-center p-8">
               <Loader2 className="mx-auto h-12 w-12 animate-spin text-primary" />
               <p className="mt-4 text-lg font-semibold">Analyzing your data...</p>
               <p className="text-muted-foreground">This will just take a moment.</p>
             </div>
           </Card>
        )}
        {!isPending && analysisResult && (
          <div className="space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <Card className="glass-card">
                <CardHeader>
                  <CardTitle className="text-xl flex items-center gap-2"><TrendingUp className="text-primary"/>Current GPA</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-5xl font-bold text-primary">{analysisResult.currentGpa.toFixed(2)}</p>
                  <p className="text-muted-foreground">Based on your current marks.</p>
                </CardContent>
              </Card>
              <Card className="glass-card">
                <CardHeader>
                  <CardTitle className="text-xl flex items-center gap-2"><Target className="text-accent" />Target GPA</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-5xl font-bold text-accent">{analysisResult.targetGpa.toFixed(2)}</p>
                   <p className="text-muted-foreground">Your goal based on target marks.</p>
                </CardContent>
              </Card>
            </div>
            
             <Card className="glass-card">
              <CardHeader>
                <CardTitle className="text-xl flex items-center gap-2"><BarChart className="text-primary"/>Performance Overview</CardTitle>
                <CardDescription>Comparing your current marks against your targets.</CardDescription>
              </CardHeader>
              <CardContent>
                 <ChartContainer config={chartConfig} className="w-full h-[250px]">
                    <RechartsBarChart data={analysisResult.subjects} accessibilityLayer>
                      <XAxis dataKey="name" tickLine={false} axisLine={false} tickMargin={8} angle={-45} textAnchor="end" height={60} />
                      <YAxis />
                      <Tooltip cursor={false} content={<ChartTooltipContent />} />
                      <Legend />
                      <Bar dataKey="marks" name="Current Marks" fill="var(--color-current)" radius={4} />
                      <Bar dataKey="target" name="Target Marks" fill="var(--color-target)" radius={4} />
                    </RechartsBarChart>
                  </ChartContainer>
              </CardContent>
            </Card>

            <Card className="glass-card">
              <CardHeader>
                <CardTitle className="text-xl flex items-center gap-2"><ListChecks className="text-primary"/>Priority Focus List</CardTitle>
                <CardDescription>Subjects to focus on for the biggest GPA impact.</CardDescription>
              </CardHeader>
              <CardContent>
                {analysisResult.prioritizedSubjects.length > 0 ? (
                  <ul className="space-y-2">
                    {analysisResult.prioritizedSubjects.map((subjectName, index) => {
                      const subjectData = analysisResult.subjects.find(s => s.name === subjectName);
                      return (
                        <li key={index} className="flex justify-between items-center p-3 bg-background/50 rounded-lg">
                          <span className="font-semibold">{index + 1}. {subjectName}</span>
                          <span className="text-sm text-primary font-mono">+{subjectData?.requiredImprovement}% required</span>
                        </li>
                      );
                    })}
                  </ul>
                ) : (
                  <p className="text-muted-foreground text-center py-4">Congratulations! You've met all your target scores.</p>
                )}
              </CardContent>
            </Card>
          </div>
        )}
        {!isPending && !analysisResult && (
          <Card className="glass-card h-full flex items-center justify-center">
            <div className="text-center p-8">
              <div className="w-24 h-24 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4 border-2 border-dashed border-primary/30">
                <BarChart className="h-12 w-12 text-primary/70" />
              </div>
              <h3 className="text-2xl font-bold font-headline">Your Analysis Awaits</h3>
              <p className="text-muted-foreground mt-2">Fill out the form to see your personalized GPA breakdown.</p>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}
