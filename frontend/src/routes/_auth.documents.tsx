import { createFileRoute } from '@tanstack/react-router'
import { useQuery } from '@tanstack/react-query';
import type { DocumentItem } from '@/types/document-types';
import { tryCatch } from '@/utils/try-catch';
import DocumentTable from '@/components/DocumentTable';
import UploadFileForm from '@/components/UploadFileForm';

export const Route = createFileRoute('/_auth/documents')({
  component: RouteComponent,
})

function RouteComponent() {


  const { data: documents, isLoading, isError, error } = useQuery<Array<DocumentItem>>({
    queryFn: () => fetchDocuments(),
    queryKey: ["documents"], 
  })

  const fetchDocuments = async (): Promise<Array<DocumentItem>> => {

    // eslint-disable-next-line no-shadow
    const [res, error] = await tryCatch(fetch(import.meta.env.VITE_API_HOST + "/document/all", {
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

    return data["urls"];
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
          documents && <DocumentTable data={documents} to_invalidate={["documents"]}/>
        )}

      </div>
    </div>
  )
}
