import {  useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { useQueryClient } from "@tanstack/react-query";
import type {SubmitHandler} from "react-hook-form";
import type {UploadFileFormValues} from "@/utils/form-schema";
import {  uploadFileSchema } from "@/utils/form-schema"
import { tryCatch } from "@/utils/try-catch"


export default function UploadFileForm({ url, to_invalidate }: { url: string, to_invalidate: Array<string> | null }) {

    const queryClient = useQueryClient()

    const { register,
        handleSubmit,
        reset,
        setError,
        formState: { errors },
    } = useForm<UploadFileFormValues>({
        resolver: zodResolver(uploadFileSchema)
    })


    const onSubmit: SubmitHandler<UploadFileFormValues> = async (form_data) => {
        console.log(form_data)

        const modifier_form_data = new FormData();

        modifier_form_data.append('file', form_data.fileList[0])


        const [res, error] = await tryCatch(fetch(import.meta.env.VITE_API_HOST + url, {
            method: "POST",
            body: modifier_form_data,
            credentials: "include"
        }));

        if (error) {
            setError("root", { message: error.message });
            return;
        }

        const data = await res.json();

        if (!res.ok) {
            setError("root", { message: data["detail"] })
            return;
        }

        if (to_invalidate != null) {
            queryClient.invalidateQueries({ queryKey: to_invalidate })
        }
        reset()
    }


    return(
        <form onSubmit={handleSubmit(onSubmit)}>
            <div className="flex flex-row">
                <input
                    type="file"
                    {...register('fileList')}
                    className="w-full text-sm text-blue-300 mr-4 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-gray-800 file:font-semibold file:bg-gray-100"
                />

                <button type="submit" className="px-2 py-1 border rounded hover:cursor-pointer">
                    Upload
                </button>
            </div>

            {errors.fileList && (
                <p className="text-red-400">{errors.fileList.message}</p>
            )}

            {errors.root && (
                <p className="text-red-400">{errors.root.message}</p>
            )}

        </form>
    )


}