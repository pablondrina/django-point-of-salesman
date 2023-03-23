# models.py
from salesman.basket.models import BaseBasket, BaseBasketItem
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.http import HttpRequest
from typing import Optional, Any, Tuple
from salesman.basket.models import BasketManager as BaseBasketManager
from salesman.core.typing import Product
from salesman.core.utils import get_salesman_model

BASKET_ID_SESSION_KEY = "BASKET_ID"


class CustomBasketManager(BaseBasketManager):

    def get_or_create_from_request(
        self,
        request: HttpRequest,
        hook_id: Optional[str] = None,
    ) -> tuple[BaseBasket, bool]:
        """
        Get basket from request or create a new one.
        If staff user is logged in and hook_id is provided, baskets can be created and retrieved for different customers using hook_id.
        Returns:
            tuple: (basket, created)
        """
        if not hasattr(request, "session"):
            request.session = {}

        if hook_id:
            session_key = f"{BASKET_ID_SESSION_KEY}_{hook_id}"
        else:
            session_key = BASKET_ID_SESSION_KEY

        try:
            session_basket_id = request.session[session_key]
            session_basket = self.get(id=session_basket_id, user=None)
        except (KeyError, self.model.DoesNotExist):
            session_basket = None

        if hasattr(request, "user") and request.user.is_authenticated and request.user.is_staff and hook_id:
            try:
                basket, created = self.get_or_create(hook_id=hook_id)
            except self.model.MultipleObjectsReturned:
                # User has multiple baskets, merge them.
                baskets = list(self.filter(hook_id=hook_id))
                basket, created = baskets[0], False
                for other in baskets[1:]:
                    basket.merge(other)

            if session_basket:
                # Merge session basket into user basket.
                basket.merge(session_basket)

            if session_key in request.session:
                # Delete session basket id from session so that it doesn't get
                # re-fetched while user is still logged in.
                del request.session[session_key]

        else:
            if hasattr(request, "user") and request.user.is_authenticated:
                basket, created = self.get_or_create(user_id=request.user.id)
            else:
                basket, created = session_basket or self.create(), not session_basket
                request.session[session_key] = basket.pk

        h = basket.hook_id
        print(f"\nCustom basket manager. Basket ID: {basket}. Created: {created}). Hook ID: {h}\n")
        return basket, created

    def get_from_request_or_none(self, request: HttpRequest, hook_id: str | None = None) -> BaseBasket | None:
        if not hasattr(request, "session"):
            request.session = {}

        if hook_id:
            session_key = f"{BASKET_ID_SESSION_KEY}_{hook_id}"
        else:
            session_key = BASKET_ID_SESSION_KEY

        try:
            session_basket_id = request.session[session_key]
            session_basket = self.get(id=session_basket_id, user=None)
        except (KeyError, self.model.DoesNotExist):
            session_basket = None

        if hasattr(request, "user") and request.user.is_authenticated and request.user.is_staff and hook_id:
            try:
                basket = self.get(hook_id=hook_id)
            except self.model.DoesNotExist:
                basket = None

            if session_basket:
                # Merge session basket into user basket if both exist
                if basket:
                    basket.merge(session_basket)
            else:
                basket = None
        else:
            basket = session_basket

        return basket


class Basket(BaseBasket):
    hook_id = models.CharField(
        _("Hook"),
        max_length=36,
        unique=True,
        blank=True,
        null=True,
    )

    objects = CustomBasketManager()

    # def add(
    #     self,
    #     product: Product,
    #     quantity: int = 1,
    #     ref: Optional[str] = None,
    #     extra: Optional[dict[str, Any]] = None,
    #     hook_id: Optional[int] = None,  # Adicionando hook_id como parâmetro opcional
    #     ) -> BaseBasketItem:
    #     """
    #     Add product to the basket.

    #     Returns:
    #         BasketItem: BasketItem instance
    #     """
    #     BasketItem = get_salesman_model("BasketItem")
    #     if not ref:
    #         ref = BasketItem.get_product_ref(product)
    #     try:
    #         item = self.items.get(ref=ref)
    #         item.quantity += quantity
    #         item.extra = extra or item.extra
    #         item.save(update_fields=["quantity", "extra", "date_updated"])
    #     except BasketItem.DoesNotExist:
    #         # Adicionando hook_id ao novo Basket
    #         basket_data = {}
    #         if hook_id:
    #             basket_data['hook_id'] = hook_id
    #         basket = Basket.objects.create(**basket_data)

    #         item = BasketItem.objects.create(
    #             basket=basket,
    #             product=product,
    #             quantity=quantity,
    #             ref=ref,
    #             extra=extra or {},
    #         )
    #     self._cached_items = None
    #     return item


class BasketItem(BaseBasketItem):
    hook_id = models.CharField(
        _("Hook id"),
        max_length=36,
        blank=True,
        null=True,
    )
