# -*- coding: utf-8 -*-

""" Finance Tables

    @copyright: 2015-2019 (c) Sahana Software Foundation
    @license: MIT

    Permission is hereby granted, free of charge, to any person
    obtaining a copy of this software and associated documentation
    files (the "Software"), to deal in the Software without
    restriction, including without limitation the rights to use,
    copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the
    Software is furnished to do so, subject to the following
    conditions:

    The above copyright notice and this permission notice shall be
    included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
    OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
    HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
    WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
    OTHER DEALINGS IN THE SOFTWARE.
"""

__all__ = ("FinExpensesModel",
           "FinPaymentServiceModel",
           )

from gluon import *
from ..s3 import *

# =============================================================================
class FinExpensesModel(S3Model):
    """ Model for Expenses """

    names = ("fin_expense",
             "fin_expense_id",
             )

    def model(self):

        T = current.T

        # -------------------------------------------------------------------------
        # Expenses
        #
        tablename = "fin_expense"
        self.define_table(tablename,
                          self.super_link("doc_id", "doc_entity"),
                          Field("name", length=128, notnull=True,
                                label = T("Short Description"),
                                ),
                          s3_date(),
                          Field("value", "double",
                                label = T("Value"),
                                represent = lambda v: \
                                    IS_FLOAT_AMOUNT.represent(v, precision=2),
                                ),
                          s3_currency(),
                          s3_comments(),
                          *s3_meta_fields(),
                          on_define = lambda table: \
                            [table.created_by.set_attributes(represent = s3_auth_user_represent_name),
                             #table.created_on.set_attributes(represent = S3DateTime.datetime_represent),
                             ]
                          )

        current.response.s3.crud_strings[tablename] = Storage(
            label_create = T("Add Expense"),
            title_display = T("Expense Details"),
            title_list = T("Expenses"),
            title_update = T("Edit Expense"),
            title_upload = T("Import Expenses"),
            label_list_button = T("List Expenses"),
            label_delete_button = T("Delete Expense"),
            msg_record_created = T("Expense added"),
            msg_record_modified = T("Expense updated"),
            msg_record_deleted = T("Expense removed"),
            msg_list_empty = T("No Expenses currently registered")
            )

        crud_form = S3SQLCustomForm("name",
                                    "date",
                                    "value",
                                    "currency",
                                    S3SQLInlineComponent(
                                        "document",
                                        name = "document",
                                        label = T("Attachments"),
                                        fields = [("", "file")],
                                    ),
                                    "comments",
                                    )

        # Resource Configuration
        self.configure(tablename,
                       crud_form = crud_form,
                       list_fields = [("date"),
                                      (T("Organization"), "created_by$organisation_id"),
                                      (T("By"), "created_by"),
                                      "name",
                                      "comments",
                                      "document.file",
                                      ],
                       super_entity = "doc_entity",
                       )

        represent = S3Represent(lookup=tablename)

        expense_id = S3ReusableField("expense_id", "reference %s" % tablename,
                                     label = T("Expense"),
                                     ondelete = "CASCADE",
                                     represent = represent,
                                     requires = IS_EMPTY_OR(
                                                IS_ONE_OF(current.db, "fin_expense.id",
                                                          represent,
                                                          orderby="fin_expense.name",
                                                          sort=True,
                                                          )),
                                     sortby = "name",
                                     )

        # ---------------------------------------------------------------------
        # Return global names to s3.*
        #
        return {"fin_expense_id": expense_id,
                }

    # -------------------------------------------------------------------------
    @staticmethod
    def defaults():
        """
            Return safe defaults in case the model has been deactivated.
        """

        dummy = S3ReusableField("dummy_id", "integer",
                                readable = False,
                                writable = False)

        return {"fin_expense_id": lambda **attr: dummy("expense_id"),
                }

# =============================================================================
class FinPaymentServiceModel(S3Model):
    """ Model for Payment Services """

    names = ("fin_payment_service",
             #"fin_payment_log", # TODO
             )

    def model(self):

        T = current.T

        # -------------------------------------------------------------------------
        # Payments Service
        #
        api_types = {"PAYPAL": "PayPal",
                     }

        tablename = "fin_payment_service"
        self.define_table(tablename,
                          Field("name",
                                requires = IS_NOT_EMPTY(),
                                ),
                          self.org_organisation_id(empty=False),
                          Field("api_type",
                                default = "PAYPAL",
                                label = T("API Type"),
                                requires = IS_IN_SET(api_types,
                                                     zero = None,
                                                     ),
                                represent = S3Represent(options = api_types,
                                                        ),
                                ),
                          Field("base_url",
                                label = T("Base URL"),
                                requires = IS_EMPTY_OR(
                                                IS_URL(mode = "generic",
                                                       allowed_schemes = ["http", "https"],
                                                       prepend_scheme = "https",
                                                       )),
                                ),
                          Field("use_proxy", "boolean",
                                default = False,
                                label = T("Use Proxy"),
                                represent = s3_yes_no_represent,
                                ),
                          Field("proxy",
                                label = T("Proxy Server"),
                                ),
                          Field("username",
                                label = T("Username (Client ID)"),
                                ),
                          Field("password",
                                label = T("Password (Client Secret)"),
                                # TODO password widget
                                ),
                          Field("token_type",
                                label = T("Token Type"),
                                readable = False,
                                writable = False,
                                ),
                          Field("access_token",
                                label = T("Access Token"),
                                readable = False,
                                writable = False,
                                ),
                          s3_datetime("token_expiry_date",
                                      default = None,
                                      label = T("Token expires on"),
                                      #readable = False,
                                      writable = False,
                                      ),
                          *s3_meta_fields())

        current.response.s3.crud_strings[tablename] = Storage(
            label_create = T("Add Payment Service"),
            title_display = T("Payment Service Details"),
            title_list = T("Payment Services"),
            title_update = T("Edit Payment Service"),
            title_upload = T("Import Payment Services"),
            label_list_button = T("List Payment Services"),
            label_delete_button = T("Delete Payment Service"),
            msg_record_created = T("Payment Service added"),
            msg_record_modified = T("Payment Service updated"),
            msg_record_deleted = T("Payment Service removed"),
            msg_list_empty = T("No Payment Services currently registered")
            )

        # TODO Implement represent using API type + org name
        represent = S3Represent(lookup=tablename)
        service_id = S3ReusableField("service_id", "reference %s" % tablename,
                                     label = T("Payment Service"),
                                     ondelete = "RESTRICT",
                                     represent = represent,
                                     requires = IS_EMPTY_OR(
                                                    IS_ONE_OF(current.db, "%s.id" % tablename,
                                                              represent,
                                                              orderby = "%s.name" % tablename,
                                                              sort = True,
                                                              )),
                                     sortby = "name",
                                     )

        # ---------------------------------------------------------------------
        # Return global names to s3.*
        #
        return {"fin_service_id": service_id,
                }

    # -------------------------------------------------------------------------
    @staticmethod
    def defaults():
        """
            Return safe defaults in case the model has been deactivated.
        """

        dummy = S3ReusableField("dummy_id", "integer",
                                readable = False,
                                writable = False,
                                )

        return {"fin_service_id": lambda **attr: dummy("service_id"),
                }

# END =========================================================================
