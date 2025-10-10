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
    .refine((fileList) => fileList.length === 1, 'Expected exactly one file.')
    // eslint-disable-next-line @typescript-eslint/no-unnecessary-condition
    .refine((fileList) => fileList[0]?.size <= MAX_UPLOAD_SIZE, 'Max file size is 40MB.')

});

export type UploadFileFormValues = z.infer<typeof uploadFileSchema>