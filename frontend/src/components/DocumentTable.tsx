import { createColumnHelper, flexRender, getCoreRowModel, useReactTable } from "@tanstack/react-table";
import DownloadButton from "./DownloadButton";
import IdPostActionButton from "./IdPostActionButton";
import type { DocumentItem } from "@/types/document-types";


export default function DocumentTable({ data, to_invalidate }: { data: Array<DocumentItem>, to_invalidate: Array<string> | null }) {

    const columnHelper = createColumnHelper<DocumentItem>()


    const columns = [
        columnHelper.accessor('key', {
            header: 'Name',
            cell: info => {
                const row = info.row.original
                return (
                    <div className="text-blue-300">
                        {row.key}
                    </div>
                )
            }
        }),
        columnHelper.accessor('status', { header: 'Status', cell: info => info.getValue() }),
        columnHelper.display({
            id: 'download',
            header: 'Download',
            cell: ({ row }) => <DownloadButton url={row.original.url} name={row.original.key} />
        }),
        columnHelper.display({
            id: 'delete',
            header: 'Delete',
            cell: ({ row }) => <IdPostActionButton url={"/document/delete"} id={row.original.id} to_invalidate={to_invalidate} action_label="Delete" />
        }),
        columnHelper.display({
            id: 'process',
            header: 'Process',
            cell: ({ row }) => <IdPostActionButton url={"/document/process"} id={row.original.id} to_invalidate={to_invalidate} action_label="Process" />
        })
    ]


    const table = useReactTable({
        data, columns, getCoreRowModel: getCoreRowModel()
    })

    return (
        <table>
            <thead>
                {table.getHeaderGroups().map(headerGroup => (
                    <tr key={headerGroup.id} className="border-b text-left">
                        {headerGroup.headers.map(header => (
                            <th key={header.id} className="px-3 py-2 text-sm text-gray-300">
                                {flexRender(header.column.columnDef.header, header.getContext())}
                            </th>
                        ))}
                    </tr>
                ))}
            </thead>
            <tbody>
                {table.getRowModel().rows.map(row => (
                    <tr key={row.id} className="border-b hover:bg-gray-900">
                        {row.getVisibleCells().map(cell => (
                            <td key={cell.id} className="px-3 py-2 text-sm">
                                {flexRender(cell.column.columnDef.cell, cell.getContext())}
                            </td>
                        ))}
                    </tr>
                ))}
            </tbody>
        </table>
    )
}