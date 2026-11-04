from app.models.transactions import CleanTransaction


def source_id_filter(stmt, source_id):
    if source_id is not None:
        stmt = stmt.where(CleanTransaction.source_id == source_id)     
    return stmt