import Link from 'next/link';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Database, LineChart, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface FeatureGridProps {
    usn?: string;
}

export function FeatureGrid({ usn }: FeatureGridProps) {
    const features = [
        {
            id: 'data-engine',
            title: 'Academic Data Engine',
            description: 'Manage student profiles, scan syllabus PDFs, and record CIE/SEE marks in the database.',
            icon: <Database className="h-8 w-8 text-primary" />,
            url: '/dashboard/engine',
            port: 8000,
            actionText: 'Launch Engine',
        },
        {
            id: 'analyzer',
            title: 'Performance Analyzer',
            description: 'Run deep analytics on your grades, simulate GPA impact, and get AI-driven academic diagnostics.',
            icon: <LineChart className="h-8 w-8 text-accent" />,
            url: '/dashboard/analyzer',
            port: 8501,
            actionText: 'Launch Analyzer',
        }
    ];

    return (
        <div className="grid gap-6 md:grid-cols-2 max-w-4xl mx-auto w-full">
            {features.map((feature) => {
                // Append USN query parameter if it exists
                const finalUrl = usn ? `${feature.url}/?usn=${encodeURIComponent(usn)}` : feature.url;

                return (
                    <Card key={feature.id} className="glass-card hover:bg-background/60 transition-colors flex flex-col h-full">
                        <CardHeader>
                            <div className="mb-4 inline-flex h-16 w-16 items-center justify-center rounded-xl bg-muted/50">
                                {feature.icon}
                            </div>
                            <CardTitle className="text-2xl font-headline">{feature.title}</CardTitle>
                            <CardDescription className="text-base mt-2">
                                {feature.description}
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="mt-auto pt-6 flex flex-col gap-2">
                            <Button asChild className="w-full text-md font-medium" size="lg">
                                <Link href={finalUrl}>
                                    {feature.actionText} <ArrowRight className="ml-2 h-4 w-4" />
                                </Link>
                            </Button>
                            <p className="text-xs text-center text-muted-foreground mt-2">
                                Embedded interface powered by Python
                            </p>
                        </CardContent>
                    </Card>
                );
            })}
        </div>
    );
}
