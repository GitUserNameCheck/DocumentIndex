

export type ContentItem = { type: "text", text: string} | { type: "image_url", image_url: {url: string}}

export type Report = {
    id: number,
    document_id: number,
    s3_filename: string,
    tag: string
}

export type ReportItem = {
    report: Report,
    url: string
}
 
export type DocumentItem = {
    id: number
    key: string
    status: string
    url: string
    reports: Array<ReportItem>
}

export type PaginationDocuments = {
    page: number
    page_size: number
    total_items: number
    documents: Array<DocumentItem>
}