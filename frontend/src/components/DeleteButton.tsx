import { useQueryClient } from "@tanstack/react-query";
import { tryCatch } from "@/utils/try-catch"


export default function DownloadButton({ url, id, to_invalidate }: { url: string, id: number, to_invalidate: Array<string> | null }) {
    const queryClient = useQueryClient()

    const onDownload = async () => {
        const [res, error] = await tryCatch(fetch(import.meta.env.VITE_API_HOST + url + `?id=${id}`, {
            method: "POST",
            credentials: "include"
        }));
        if (error || !res.ok) {
            alert('Deletion failed')
            return
        }

        if(to_invalidate != null){
            queryClient.invalidateQueries({queryKey: to_invalidate})
        }
    }

    return (
        <button onClick={onDownload} className="px-2 py-1 border rounded text-sm hover:cursor-pointer">
            Delete
        </button>
    )
}