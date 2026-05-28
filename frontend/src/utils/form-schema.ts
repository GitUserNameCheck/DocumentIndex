import { z } from "zod";

export const authSchema = z.object({
    username: z.string().min(3, "Username must be at least 3 characters"),
    password: z.string().min(6, "Password must be at least 6 characters"),
});

export type AuthFormValues = z.infer<typeof authSchema>


const MAX_UPLOAD_SIZE = 40 * 1024 * 1024

export const uploadFileSchema = z.object({
    fileList: z
    .instanceof(FileList)
    .refine((fileList) => fileList.length > 0, "Please select at least one file.")
    .refine(
        (fileList) =>
            Array.from(fileList).every(
                (file) => file.size <= MAX_UPLOAD_SIZE
            ),
        "Each file must be smaller than 40MB."
    )

});

export type UploadFileFormValues = z.infer<typeof uploadFileSchema>