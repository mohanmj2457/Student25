import Link from "next/link";
import { Button } from "@/components/ui/button";
import { BarChart, BrainCircuit, TrendingUp, ArrowRight } from "lucide-react";
import { ShaderAnimation } from "@/components/gpa/ShaderAnimation";
import GlowHero from "@/components/gpa/GlowHero";

const features = [
  {
    icon: <BarChart className="h-10 w-10 text-primary" />,
    title: "In-depth GPA Analysis",
    description: "Visualize your academic performance, track your GPA, and see where you stand.",
  },
  {
    icon: <BrainCircuit className="h-10 w-10 text-primary" />,
    title: "AI-Powered Insights",
    description: "Receive personalized recommendations and study priorities powered by AI.",
  },
  {
    icon: <TrendingUp className="h-10 w-10 text-primary" />,
    title: "Boost Your Performance",
    description: "Focus on subjects that need the most attention to improve your grades effectively.",
  },
];

export default function Home() {
  return (
    <>
      {/* Hero Section */}
      <section className="relative w-full h-screen flex items-center justify-center text-center overflow-hidden">
        <div className="absolute inset-0 z-0">
          <ShaderAnimation />
        </div>
        <div className="relative z-10 container mx-auto px-4 md:px-6">
          <div className="max-w-3xl mx-auto text-center space-y-6">
             <GlowHero glowText="Padhloo" glowTextSize="xl" className="mb-4" />
            <p className="text-lg leading-8 text-muted-foreground md:text-xl">
              Unlock Your Academic Potential.
              <br/>
              Your personal AI study partner.
            </p>
            <div className="mt-10 flex items-center justify-center gap-x-6">
              <Button asChild size="lg">
                <Link href="/login">Get Started <ArrowRight className="ml-2 h-5 w-5" /></Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="w-full py-20 md:py-24 bg-zinc-900/50 border-y border-border">
        <div className="container mx-auto px-4 md:px-6">
          <div className="flex flex-col items-center justify-center space-y-4 text-center">
            <div className="space-y-2">
              <div className="inline-block rounded-lg bg-muted px-3 py-1 text-sm">Key Features</div>
              <h2 className="text-3xl font-bold tracking-tighter sm:text-5xl font-headline">Study Smarter, Not Harder</h2>
              <p className="max-w-[900px] text-muted-foreground md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
                Padhloo provides you with the tools and insights you need to excel in your studies.
              </p>
            </div>
          </div>
          <div className="mx-auto grid max-w-5xl items-start gap-12 py-12 lg:grid-cols-3">
            {features.map((feature, index) => (
              <div key={index} className="grid gap-4 text-center">
                <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 border border-primary/20">
                  {feature.icon}
                </div>
                <div className="space-y-2">
                  <h3 className="text-xl font-bold font-headline">{feature.title}</h3>
                  <p className="text-muted-foreground">{feature.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
      
      {/* How It Works Section */}
      <section id="how-it-works" className="w-full py-20 md:py-24 lg:py-32">
        <div className="container mx-auto px-4 md:px-6">
          <div className="flex flex-col items-center justify-center space-y-4 text-center">
              <div className="space-y-2">
                <div className="inline-block rounded-lg bg-muted px-3 py-1 text-sm">How It Works</div>
                <h2 className="text-3xl font-bold tracking-tighter sm:text-5xl font-headline">A Simple Path to Success</h2>
                <p className="max-w-[900px] text-muted-foreground md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
                  In just a few simple steps, you can get a complete analysis of your academic standing.
                </p>
              </div>
            </div>
            <div className="relative py-12 md:py-20">
               <div className="absolute top-1/2 left-0 w-full h-0.5 bg-border -translate-y-1/2 hidden md:block"></div>
               <div className="relative grid grid-cols-1 md:grid-cols-3 gap-12 md:gap-8">
                <div className="flex flex-col items-center text-center gap-4">
                  <div className="w-16 h-16 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-2xl font-bold border-8 border-background z-10">1</div>
                  <h3 className="text-xl font-bold font-headline mt-2">Input Your Grades</h3>
                  <p className="text-muted-foreground">Quickly enter your subjects, credits, and current marks.</p>
                </div>
                 <div className="flex flex-col items-center text-center gap-4">
                  <div className="w-16 h-16 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-2xl font-bold border-8 border-background z-10">2</div>
                  <h3 className="text-xl font-bold font-headline mt-2">Get Instant Analysis</h3>
                  <p className="text-muted-foreground">Receive your current GPA and a prioritized list of subjects to focus on.</p>
                </div>
                 <div className="flex flex-col items-center text-center gap-4">
                  <div className="w-16 h-16 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-2xl font-bold border-8 border-background z-10">3</div>
                  <h3 className="text-xl font-bold font-headline mt-2">Achieve Your Goals</h3>
                  <p className="text-muted-foreground">Use the insights to study efficiently and reach your target GPA.</p>
                </div>
               </div>
            </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="w-full py-20 md:py-24 border-t border-border">
        <div className="container mx-auto px-4 md:px-6">
          <div className="glass-card rounded-xl p-8 md:p-12">
            <div className="max-w-3xl mx-auto text-center space-y-6">
              <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl font-headline">Ready to Elevate Your Grades?</h2>
              <p className="text-muted-foreground md:text-xl/relaxed">
                Stop guessing and start analyzing. Get the clarity you need to succeed.
              </p>
              <div className="mt-6">
                <Button asChild size="lg" className="font-bold text-lg py-6 bg-primary text-primary-foreground hover:bg-primary/90 transition-all duration-300 hover:glow-primary">
                  <Link href="/login">Analyze My GPA Now <ArrowRight className="ml-2 h-5 w-5" /></Link>
                </Button>
              </div>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
