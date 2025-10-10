import { tryCatch } from "@/utils/try-catch"


export default function DownloadButton({ url, name }: { url: string, name: string }) {

    const onDownload = async () => {
        const [res, error] = await tryCatch(fetch(url))
        if (error || !res.ok) {
            alert('Download failed')
            return
        }

        const blob = await res.blob()
        const link = document.createElement('a')
        link.href = window.URL.createObjectURL(blob)
        link.download = name
        document.body.appendChild(link)
        link.click()
        link.remove()
    }

    return (
        <button onClick={onDownload} className="px-2 py-1 border rounded text-sm hover:cursor-pointer">
            Download
        </button>
    )
}