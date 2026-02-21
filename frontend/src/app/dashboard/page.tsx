import { FeatureGrid } from "@/components/dashboard/FeatureGrid";
import { ShaderAnimation } from "@/components/gpa/ShaderAnimation";

export default async function DashboardPage(props: { searchParams: Promise<{ [key: string]: string | string[] | undefined }> }) {
    const searchParams = await props.searchParams;
    const usnParam = searchParams.usn;
    const usn = typeof usnParam === 'string' ? usnParam : undefined;

    return (
        <div className="relative min-h-screen w-full flex flex-col items-center pt-24 pb-12 px-4">
            {/* Background Animation */}
            <div className="absolute inset-0 z-0">
                <ShaderAnimation />
            </div>

            {/* Content */}
            <div className="relative z-10 w-full max-w-5xl mx-auto space-y-12">
                <div className="text-center space-y-4">
                    <h1 className="text-4xl md:text-5xl font-bold font-headline tracking-tighter">
                        Welcome to Padhloo
                    </h1>
                    <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                        {usn ? `Logged in as ${usn}. ` : ''}Select a tool below to manage your academic data or run advanced performance analytics.
                    </p>
                </div>

                <FeatureGrid usn={usn} />
            </div>
        </div>
    );
}
