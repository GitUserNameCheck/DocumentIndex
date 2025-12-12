import {  createColumnHelper, flexRender, getCoreRowModel, useReactTable } from "@tanstack/react-table";
import DownloadButton from "./DownloadButton";
import IdPostActionButton from "./IdPostActionButton";
import type {PaginationState} from "@tanstack/react-table";
import type { DocumentItem, PaginationDocuments } from "@/types/document-types";


export default function DocumentTable({ paginationDocuments, toInvalidate, pagination, setPagination }: { paginationDocuments: PaginationDocuments, toInvalidate: Array<string> | null, pagination: PaginationState, setPagination: React.Dispatch<React.SetStateAction<PaginationState>> }) {

    const columnHelper = createColumnHelper<DocumentItem>()


    const columns = [
        columnHelper.display({
            id: "order",
            header: "#",
            cell: ({ row, table }) => {
                const pageIndex = table.getState().pagination.pageIndex
                const pageSize = table.getState().pagination.pageSize

                return pageIndex * pageSize + row.index + 1
            }
        }),
        columnHelper.accessor('key', {
            header: 'Name',
            cell: info => {
                const row = info.row.original
                return (
                    <div>
                        <button
                            onClick={() => window.open(row.url, "_blank")}
                            className="text-blue-300 underline hover:cursor-pointer"
                        >
                            {row.key}
                        </button>
                    
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
            cell: ({ row }) => <IdPostActionButton url={"/document/delete"} id={row.original.id} toInvalidate={toInvalidate} actionLabel="Delete" />
        }),
        columnHelper.display({
            id: 'process',
            header: 'Process',
            cell: ({ row }) => <IdPostActionButton url={"/document/process"} id={row.original.id} toInvalidate={toInvalidate} actionLabel="Process" />
        })
    ]
    
    const table = useReactTable({
        data: paginationDocuments.documents, 
        columns, 
        getCoreRowModel: getCoreRowModel(),
        manualPagination: true,
        rowCount: paginationDocuments.total_items,
        state:{
            pagination,
        },
        onPaginationChange: setPagination
    })

    return (
        <div>
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
            <div className="flex items-center gap-3 mt-4 p-3 bg-slate-800 rounded-xl shadow-md border border-slate-700">
                <button
                    className="px-3 py-1 rounded-lg bg-slate-700 hover:bg-slate-600 disabled:opacity-40 disabled:cursor-not-allowed transition"
                    onClick={() => table.firstPage()}
                    disabled={!table.getCanPreviousPage()}
                >
                    {'<<'}
                </button>

                <button
                    className="px-3 py-1 rounded-lg bg-slate-700 hover:bg-slate-600 disabled:opacity-40 disabled:cursor-not-allowed transition"
                    onClick={() => table.previousPage()}
                    disabled={!table.getCanPreviousPage()}
                >
                    {'<'}
                </button>

                <span className="text-gray-300 text-sm">
                    Page{' '}
                    <strong className="text-white">
                        {table.getState().pagination.pageIndex + 1}
                    </strong>{' '}
                    of{' '}
                    <strong className="text-white">
                        {table.getPageCount().toLocaleString()}
                    </strong>
                </span>

                <button
                    className="px-3 py-1 rounded-lg bg-slate-700 hover:bg-slate-600 disabled:opacity-40 disabled:cursor-not-allowed transition"
                    onClick={() => table.nextPage()}
                    disabled={!table.getCanNextPage()}
                >
                    {'>'}
                </button>

                <button
                    className="px-3 py-1 rounded-lg bg-slate-700 hover:bg-slate-600 disabled:opacity-40 disabled:cursor-not-allowed transition"
                    onClick={() => table.lastPage()}
                    disabled={!table.getCanNextPage()}
                >
                    {'>>'}
                </button>

                <span className="flex items-center gap-2 ml-4 text-gray-300 text-sm">
                    Go to page:
                    <input
                        type="number"
                        min="1"
                        max={table.getPageCount()}
                        defaultValue={table.getState().pagination.pageIndex + 1}
                        onChange={e => {
                            const raw = Number(e.target.value)

                            if (Number.isNaN(raw)) return

                            const pageCount = table.getPageCount()
                            const page = Math.min(Math.max(raw - 1, 0), pageCount - 1)

                            table.setPageIndex(page)
                        }}
                        className="w-16 px-2 py-1 bg-slate-700 border border-slate-600 rounded-lg text-gray-200 focus:outline-none focus:ring-2 focus:ring-cyan-600"
                    />
                </span>

                <select
                    value={table.getState().pagination.pageSize}
                    onChange={e => table.setPageSize(Number(e.target.value))}
                    className="px-2 py-1 bg-slate-700 border border-slate-600 rounded-lg text-gray-200 focus:outline-none focus:ring-2 focus:ring-cyan-600"
                >
                    {[10, 20, 50, 100].map(size => (
                        <option key={size} value={size}>
                            Show {size}
                        </option>
                    ))}
                </select>
            </div>
        </div>
    )
}