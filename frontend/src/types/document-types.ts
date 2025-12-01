

export type DocumentItem = {
    id: number
    key: string
    status: string
    url: string
}

export type PaginationDocuments = {
    page: number
    page_size: number
    total_items: number
    documents: Array<DocumentItem>
}