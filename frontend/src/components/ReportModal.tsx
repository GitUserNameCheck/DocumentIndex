import { useState } from "react"
import type {
    ContentItem,
    DocumentItem,
    ReportItem
} from "@/types/document-types"
import { tryCatch } from "@/utils/try-catch"

type SearchResponse = {
    result: string
    items: Array<ContentItem>
}

export default function ReportModal({
    document,
    onClose,
}: {
    document: DocumentItem
    onClose: () => void
}) {
    const [selectedReport, setSelectedReport] =
        useState<ReportItem | null>(null)

    const [prompt, setPrompt] = useState("")
    const [searchText, setSearchText] = useState("")
    const [searchResponse, setSearchResponse] = useState<SearchResponse | null>(null)
    const [loading, setLoading] = useState(false)

    const evidence = searchResponse?.items ?? []

    async function handleSearch() {
        if (!selectedReport) return

        setSearchResponse(null)
        setLoading(true)

        const params = new URLSearchParams({
            "report_id": selectedReport.report.id.toString(),
            "prompt": prompt,
            "search_text": searchText
        });

        try {
            const [res, error] = await tryCatch(fetch(import.meta.env.VITE_API_HOST + `/document/report_points_based_search?${params.toString()}`, {
                method: "GET",
                credentials: "include",
                headers: {
                    "Content-Type": "application/json",
                },
                // body: JSON.stringify({
                //     "report_id": selectedReport.report.id,
                //     "prompt": prompt,
                //     "search_text": searchText
                // }),
            }))


            if (error) {
                alert(error.message);
                return;
            }

            const data = await res.json();

            console.log(data)

            if (!res.ok) {
                alert(data["detail"])
                return;
            }

            setSearchResponse(data)
            
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
            <div className="w-[1500px] h-[800px] bg-slate-900 rounded-2xl border border-slate-700 p-6 overflow-hidden flex flex-col">

                {/* HEADER */}
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-xl font-semibold text-white">
                        Reports for {document.key}
                    </h2>

                    <button
                        onClick={onClose}
                        className="px-3 py-1 rounded bg-slate-700 hover:bg-slate-600"
                    >
                        Close
                    </button>
                </div>

                <div className="grid grid-cols-2 gap-6 flex-1 overflow-hidden">

                    {/* LEFT SIDE */}
                    <div className="flex flex-col overflow-hidden">

                        <h3 className="text-lg text-white mb-2">
                            Reports
                        </h3>

                        <div className="overflow-auto border border-slate-700 rounded-xl">
                            <table className="w-full">
                                <thead className="bg-slate-800">
                                    <tr>
                                        <th className="p-2 text-left">
                                            Tag
                                        </th>

                                        <th className="p-2 text-left">
                                            File
                                        </th>

                                        <th className="p-2">
                                            Select
                                        </th>
                                    </tr>
                                </thead>

                                <tbody>
                                    {document.reports.map(report => (
                                        <tr
                                            key={report.report.id}
                                            className="border-t border-slate-700"
                                        >
                                            <td className="p-2">
                                                {report.report.tag}
                                            </td>

                                            <td className="p-2">
                                                {report.url ? (  
                                                    <button
                                                        onClick={() => window.open(report.url, "_blank", "noopener,noreferrer")}
                                                        className="text-blue-300 underline hover:cursor-pointer"
                                                    >
                                                        {report.report.s3_filename}
                                                    </button> 
                                                ) : (report.report.s3_filename)
                                                }
                                            </td>

                                            <td className="p-2 flex justify-center items-center">
                                                <button
                                                    onClick={() => setSelectedReport(report)}
                                                    disabled={loading}
                                                    className={`w-6 h-6 rounded border transition-all ${selectedReport?.report.id === report.report.id
                                                            ? "bg-cyan-700 border-cyan-700 text-white"
                                                            : "border-slate-500 hover:border-slate-400"
                                                        }`}
                                                >
                                                    {selectedReport?.report.id === report.report.id && "✓"}
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>

                        {/* PROMPT */}
                        <div className="mt-4 flex flex-col gap-3 p-1">

                            <textarea
                                value={prompt}
                                onChange={e =>
                                    setPrompt(e.target.value)
                                }
                                placeholder="Provide prompt for the llm..."
                                className="w-full h-32 bg-slate-800 border border-slate-700 rounded-xl p-3 text-white resize-none"
                            />

                            <textarea
                                value={searchText}
                                onChange={e =>
                                    setSearchText(e.target.value)
                                }
                                placeholder="Ask something about this report..."
                                className="w-full h-40 bg-slate-800 border border-slate-700 rounded-xl p-3 text-white resize-none"
                            />

                            <button
                                onClick={handleSearch}
                                disabled={!selectedReport || loading}
                                className="px-2 py-1 border rounded hover:cursor-pointer disabled:opacity-40"
                            >
                                {loading
                                    ? "Searching..."
                                    : "Search"}
                            </button>
                        </div>
                    </div>

                    {/* RIGHT SIDE */}
                    <div className="flex flex-col overflow-hidden">

                        <h3 className="text-lg text-white mb-2">
                            Result
                        </h3>

                        <div className="flex-1 overflow-auto bg-slate-800 border border-slate-700 rounded-xl p-4 text-gray-200 whitespace-pre-wrap">
                            {searchResponse?.result || "No result yet"}
                        </div>

                        <h3 className="text-lg text-white mt-4 mb-2">
                            Evidence / Source Items
                        </h3>

                        <div className="h-100 overflow-auto bg-slate-800 border border-slate-700 rounded-xl p-4">
                            {evidence.length === 0 ? (
                                <div className="text-gray-400">
                                    No evidence yet
                                </div>
                            ) : (
                                <div className="flex flex-col gap-3">
                                        {evidence.map((item, index) => {
                                            if (item.type === "text") {
                                                return (
                                                    <div
                                                        key={index}
                                                        className="p-3 rounded-lg bg-slate-700 text-sm text-gray-200 whitespace-pre-wrap"
                                                    >
                                                        {item.text}
                                                    </div>
                                                )
                                            }

                                            return (
                                                <div
                                                    key={index}
                                                    className="p-3 rounded-lg bg-slate-700"
                                                >
                                                    <img
                                                        src={item.image_url.url}
                                                        alt="Evidence"
                                                        className="max-w-full rounded-lg"
                                                    />
                                                </div>
                                            )
                                        })}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}