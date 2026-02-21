export default function EngineWrapperPage() {
    const engineUrl = process.env.NEXT_PUBLIC_ENGINE_URL || "http://localhost:8000";
    return (
        <div className="w-full h-screen overflow-hidden bg-background">
            <iframe
                src={`${engineUrl}?v=2`}
                className="w-full h-full border-none"
                title="Academic Data Engine"
                sandbox="allow-same-origin allow-scripts allow-forms allow-popups"
            />
        </div>
    );
}

