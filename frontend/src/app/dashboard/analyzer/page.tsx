export default async function AnalyzerWrapperPage(props: { searchParams: Promise<{ [key: string]: string | string[] | undefined }> }) {
    const searchParams = await props.searchParams;
    const usnParam = searchParams.usn;
    const usn = typeof usnParam === 'string' ? usnParam : undefined;

    const analyzerBase = process.env.NEXT_PUBLIC_ANALYZER_URL || "http://localhost:8501";
    const streamlitUrl = usn
        ? `${analyzerBase}/?usn=${encodeURIComponent(usn)}`
        : analyzerBase;

    return (
        <div className="w-full h-screen overflow-hidden bg-background">
            <iframe
                src={streamlitUrl}
                className="w-full h-full border-none"
                title="Academic Performance Analyzer"
                sandbox="allow-same-origin allow-scripts allow-forms allow-popups allow-downloads"
            />
        </div>
    );
}

