import { useQueryClient } from "@tanstack/react-query";
import { tryCatch } from "@/utils/try-catch"


export default function IdPostActionButton({ url, id, to_invalidate, action_label }: { url: string, id: number, to_invalidate: Array<string> | null, action_label: string }) {
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

        if(to_invalidate != null){
            queryClient.invalidateQueries({queryKey: to_invalidate})
        }
    }

    return (
        <button onClick={onClick} className="px-2 py-1 border rounded text-sm hover:cursor-pointer">
            {action_label}
        </button>
    )
}