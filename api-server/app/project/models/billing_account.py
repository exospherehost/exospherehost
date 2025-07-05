from enum import Enum
from pydantic import BaseModel, Field


class TaxInformationTypeEnum(str, Enum):
    GST = "GST"
    VAT = "VAT"
    EIN = "EIN"
    PAN = "PAN"


class BillingAccount(BaseModel):

    company_name: str = Field(default="", description="Name of the company")

    billing_address: str = Field(default="", description="Billing address of the company")

    tax_number_type: TaxInformationTypeEnum = Field(default="", description="Type of tax information")

    tax_number: str = Field(default="", description="Tax information of the company")

    country: str = Field(default="", description="Country of the company")