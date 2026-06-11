from fastapi import HTTPException

# Magic bytes (file signatures)
PDF_SIGNATURE = b"%PDF"
DOCX_SIGNATURE = b"PK\x03\x04"

def verify_file_signature(content: bytes, filename: str) -> None:
    """
    Verify if the file signature matches its extension to prevent spoofing.
    Raises HTTPException (400) if signature does not match.
    """
    filename_lower = filename.lower()
    
    # Needs at least 4 bytes to check signature
    if len(content) < 4:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is too small or empty."
        )
        
    first_bytes = content[:4]
    
    if filename_lower.endswith(".pdf"):
        if first_bytes != PDF_SIGNATURE:
            raise HTTPException(
                status_code=400,
                detail="File content does not match a valid PDF layout (invalid signature)."
            )
            
    elif filename_lower.endswith(".docx"):
        if first_bytes != DOCX_SIGNATURE:
            raise HTTPException(
                status_code=400,
                detail="File content does not match a valid Word Document (.docx) layout."
            )
            
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Only PDF and DOCX files are allowed."
        )
