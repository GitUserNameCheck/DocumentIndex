
export default function SkeletonTable({ rows }: { rows: number}) {

    return (
        <table>
            <thead>
                <tr className="border-b text-left">
                    {["#", "Name", "Status", "Download", "Reports"].map((h) => (
                        <th key={h} className="px-3 py-2 text-gray-300">
                            {h}
                        </th>
                    ))}
                </tr>
            </thead>

            <tbody>
                {Array.from({ length: rows }).map((_, i) => (
                    <tr key={i} className="border-b">
                        
                        {/* Checkmark */}
                        <td className="px-3 py-2">
                            <div className="h-[1rem] w-[25px] bg-gray-700 rounded animate-pulse" />
                        </td>

                        {/* Order */}
                        <td className="px-3 py-2">
                            <div className="h-[1rem] w-[25px] bg-gray-700 rounded animate-pulse" />
                        </td>

                        {/* Name */}
                        <td className="px-3 py-2">
                            <div className="h-[1rem] w-40 bg-gray-700 rounded animate-pulse" />
                        </td>

                        {/* Status */}
                        <td className="px-3 py-2">
                            <div className="h-[1rem] w-40 bg-gray-700 rounded animate-pulse" />
                        </td>

                        {/* Download */}
                        <td className="px-3 py-2">
                            <div className="h-[1rem] w-30 bg-gray-700 rounded animate-pulse" />
                        </td>

                        {/* Reports */}
                        <td className="px-3 py-2">
                            <div className="h-[1rem] w-30 bg-gray-700 rounded animate-pulse" />
                        </td>
                    </tr>
                ))}
            </tbody>
        </table>
    )
}