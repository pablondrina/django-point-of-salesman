from __future__ import annotations

from typing import Any

from django.http import HttpRequest
from django.http.response import HttpResponseBase
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from rest_framework import mixins, status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response

from salesman.conf import app_settings
from salesman.core.utils import get_salesman_model

from .payment import PaymentError, payment_methods_pool
from .serializers import CheckoutSerializer

from rest_framework.exceptions import ValidationError

Basket = get_salesman_model("Basket")


class CheckoutViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    Checkout API endpoint.
    """

    serializer_class = CheckoutSerializer

    def get_view_name(self) -> str:
        name = super().get_view_name()
        if name == "Checkout List":
            return "Checkout"
        return name

    def get_queryset(self) -> None:
        pass

    # def get_serializer_context(self) -> dict[str, Any]:
    #     context = super().get_serializer_context()
    #     context["basket"], _ = Basket.objects.get_or_create_from_request(self.request)
    #     context["basket"].update(self.request)
    #     return context

    # def get_serializer_context(self) -> dict[str, Any]:
    #     context = super().get_serializer_context()
    #     hook_id = self.request.data.get('hook_id', None)
    #     basket = Basket.objects.get_from_request_or_none(self.request, hook_id)

    #     if basket is None:
    #         raise ValidationError({"hook_id": _("No basket found for the given hook_id.")})

    #     context["basket"] = basket
    #     context["basket"].update(self.request)
    #     return context

    def get_serializer_context(self) -> dict[str, Any]:
        context = super().get_serializer_context()
        hook_id = self.request.data.get("hook_id")

        if hook_id:
            try:
                context["basket"] = Basket.objects.get(hook_id=hook_id)
            except Basket.DoesNotExist:
                pass  # A validação do hook_id será tratada no CheckoutSerializer
        else:
            context["basket"], _ = Basket.objects.get_or_create_from_request(self.request)

        if "basket" in context:
            context["basket"].update(self.request)
        return context




    def check_permissions(self, request: Request) -> None:
        super().check_permissions(request)

        if not app_settings.SALESMAN_ALLOW_ANONYMOUS_USER_CHECKOUT and not bool(
            request.user and request.user.is_authenticated
        ):
            raise PermissionDenied(detail=_("Anonymous checkout not allowed."))

    @method_decorator(never_cache)
    def dispatch(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponseBase:
        return super().dispatch(request, *args, **kwargs)

    # def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
    #     """
    #     Process the checkout, handle ``PaymentError``.
    #     """
    #     try:
    #         return super().create(request, *args, **kwargs)
    #     except PaymentError as e:
    #         return Response({"detail": str(e)}, status=status.HTTP_402_PAYMENT_REQUIRED)

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Process the checkout, handle ``PaymentError`` and ``ValidationError``.
        """
        try:
            return super().create(request, *args, **kwargs)
        except PaymentError as e:
            return Response({"detail": str(e)}, status=status.HTTP_402_PAYMENT_REQUIRED)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)




    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Show a list of payment methods with errors if they exist.
        """
        instance = {
            "payment_methods": payment_methods_pool.get_payments("basket", request)
        }
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
