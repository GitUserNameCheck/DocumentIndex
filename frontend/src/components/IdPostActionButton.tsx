import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import type { DocumentItem } from "@/types/document-types";
import { tryCatch } from "@/utils/try-catch"


export default function IdPostActionButton(
    {
        url, 
        rows, 
        toInvalidate, 
        actionLabel, 
        toastLabel,
        toastCompleteLabel
    } : { 
        url: string, 
        rows: Array<DocumentItem>, 
        toInvalidate: Array<string> | null, 
        actionLabel: string, 
        toastLabel: string ,
        toastCompleteLabel: string
    }) {

    const queryClient = useQueryClient()

    const onClick = async () => {

        for (const row of rows) {

            const toastId = toast.loading(toastLabel, {
                closeButton: true,
                description: row.key
            });

            const [res, error] = await tryCatch(fetch(import.meta.env.VITE_API_HOST + url + `?id=${row.id}`, {
                method: "POST",
                credentials: "include"
            }));

            if (error) {
                alert(error.message);
                toast.dismiss(toastId);
                return;
            }

            const data = await res.json();

            if (!res.ok) {
                alert(data["detail"])
                toast.dismiss(toastId);
                return;
            }

            toast.dismiss(toastId);

            toast.success(toastCompleteLabel + row.key, {
                closeButton: true,
            });

        }

        if (toInvalidate != null){
            queryClient.invalidateQueries({ queryKey: toInvalidate })
        }
    }

    return (
        <button onClick={onClick} className="px-2 py-1 border rounded hover:cursor-pointer">
            {actionLabel}
        </button>
    )
}