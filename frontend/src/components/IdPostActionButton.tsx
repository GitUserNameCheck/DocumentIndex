import { useQueryClient } from "@tanstack/react-query";
import { tryCatch } from "@/utils/try-catch"


export default function IdPostActionButton({ url, id, toInvalidate, actionLabel }: { url: string, id: number, toInvalidate: Array<string> | null, actionLabel: string }) {
    const queryClient = useQueryClient()

    const onClick = async () => {
        const [res, error] = await tryCatch(fetch(import.meta.env.VITE_API_HOST + url + `?id=${id}`, {
            method: "POST",
            credentials: "include"
        }));

        if (error) {
            alert(error.message);
            return;
        }

        const data = await res.json();

        if (!res.ok) {
            alert(data["detail"])
            return;
        }

        if (toInvalidate != null){
            queryClient.invalidateQueries({ queryKey: toInvalidate })
        }
    }

    return (
        <button onClick={onClick} className="px-2 py-1 border rounded text-sm hover:cursor-pointer">
            {actionLabel}
        </button>
    )
}