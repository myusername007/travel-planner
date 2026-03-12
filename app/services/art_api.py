import httpx

BASE_URL = "https://api.artic.edu/api/v1"


async def get_artwork(external_id: int) -> dict | None:

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"{BASE_URL}/artworks/{external_id}?fields=id,title") # fetch artwork by id
            if response.status_code == 200: # return data or None
                return response.json().get("data") 
            return None
        except httpx.RequestError:
            return None