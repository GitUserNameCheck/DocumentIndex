import { createFileRoute } from '@tanstack/react-router'
import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import type { PaginationDocuments } from '@/types/document-types';
import type { PaginationState } from '@tanstack/react-table';
import { tryCatch } from '@/utils/try-catch';
import DocumentTable from '@/components/DocumentTable';
import UploadFileForm from '@/components/UploadFileForm';

export const Route = createFileRoute('/_auth/documents')({
  component: RouteComponent,
})

function RouteComponent() {

  const [pagination, setPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 10,
  })

  const { data: documents, isLoading, isError, error } = useQuery<PaginationDocuments>({
    queryFn: () => fetchDocuments(pagination),
    queryKey: ["documents", pagination], 
  })

  const fetchDocuments = async (
  {
    pageIndex,
    pageSize,
  } : {
    pageIndex: number
    pageSize: number
  }): Promise<PaginationDocuments> => {

    const url = new URL(import.meta.env.VITE_API_HOST + "/document/get")

    url.searchParams.set("page", String(pageIndex + 1))
    url.searchParams.set("page_size", String(pageSize))

    // eslint-disable-next-line no-shadow
    const [res, error] = await tryCatch(fetch(url.toString(), {
      method: "GET",
      credentials: "include"
    }));

    if (error) {
      throw new Error(error.message)
    }

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data["detail"])
    }

    return data;
  }

  return (
    <div className="flex justify-center mt-20">

      <div className="flex flex-col items-center bg-slate-800 p-3 rounded-2xl shadow-lg">

        <h1 className="text-2xl mb-3">Documents</h1>

        <div className=" p-4 rounded w-full">
          <UploadFileForm url={'/document/upload'} to_invalidate={["documents"]} />
        </div>

        {isLoading ? (
          <div>Loading…</div>
        ) : isError ? (
            <p className="text-red-400">{error.message}</p>
        ) : (
          documents && <DocumentTable paginationDocuments={documents} toInvalidate={["documents"]} pagination={pagination} setPagination={setPagination} />
        )}

      </div>
    </div>
  )
}
