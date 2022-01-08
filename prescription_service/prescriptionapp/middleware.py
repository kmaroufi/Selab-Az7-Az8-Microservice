import asyncio

from django.http import JsonResponse
from django.utils.decorators import sync_and_async_middleware

from prescription_service.settings import INTERNAL_SERVICE_TOKEN


@sync_and_async_middleware
def token_check_middleware(get_response):
    if asyncio.iscoroutinefunction(get_response):
        async def middleware(request):
            try:
                if request.headers.get('Authorization').split()[1] == INTERNAL_SERVICE_TOKEN:
                    response = await get_response(request)
                    return response
                else:
                    return JsonResponse({'result': 'error', 'message': 'invalid token'})
            except:
                return JsonResponse({'result': 'error', 'message': 'invalid token'})
    else:
        def middleware(request):
            try:
                if request.headers.get('Authorization').split()[1] == INTERNAL_SERVICE_TOKEN:
                    response = get_response(request)
                    return response
                else:
                    return JsonResponse({'result': 'error', 'message': 'invalid token'})
            except:
                return JsonResponse({'result': 'error', 'message': 'invalid token'})

    return middleware
