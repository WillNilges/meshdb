from typing import Optional

from meshapi import models
from meshdb.utils.spreadsheet_import.csv_load import SpreadsheetRow, SpreadsheetStatus


def translate_spreadsheet_status_to_db_status(
    status: SpreadsheetStatus,
) -> models.Install.InstallStatus:

    if status in {
        SpreadsheetStatus.interested,
        SpreadsheetStatus.toBeScheduled,
        SpreadsheetStatus.notContactedYet,
        SpreadsheetStatus.noStatus,
        # TODO: Is this right? There are a lot of old "no status" rows
        #  & maybe we don't want these to show as OPEN?
    }:
        return models.Install.InstallStatus.OPEN
    elif status in {SpreadsheetStatus.scheduled}:
        return models.Install.InstallStatus.SCHEDULED
    elif status in {SpreadsheetStatus.nnAssigned}:
        return models.Install.InstallStatus.NN_ASSIGNED
    elif status in {SpreadsheetStatus.noLos}:
        return models.Install.InstallStatus.BLOCKED
    elif status in {SpreadsheetStatus.installed}:
        return models.Install.InstallStatus.ACTIVE
    elif status in {SpreadsheetStatus.poweredOff}:
        return models.Install.InstallStatus.INACTIVE
    elif status in {
        SpreadsheetStatus.abandoned,
        SpreadsheetStatus.notInterested,
        SpreadsheetStatus.unsubscribe,
        SpreadsheetStatus.invalid,
        SpreadsheetStatus.noReply,
        SpreadsheetStatus.dupe,
    }:
        return models.Install.InstallStatus.CLOSED

    raise ValueError(
        f"Invalid spreadsheet status: {status} do you need to add another case to this function?"
    )


def get_or_create_install(row: SpreadsheetRow) -> Optional[models.Install]:
    return models.Install(
        install_number=row.id,
        network_number=row.nn,
        install_status=translate_spreadsheet_status_to_db_status(row.status),
        ticket_id=None,  # TODO: Figure out if we can export data from OSTicket to back-fill this
        request_date=row.request_date.date(),
        install_date=row.installDate,
        abandon_date=row.abandonDate,
        unit=row.apartment,
        roof_access=row.roofAccess,
        referral=row.referral,
        notes=f"Spreadsheet Notes:\n"
        f"{row.notes if row.notes else None}\n\n"
        f"Spreadsheet Notes2:\n"
        f"{row.notes2 if row.notes2 else None}\n\n"
        f"Spreadsheet Install Notes:\n"
        f"{row.installNotes if row.installNotes else None}\n\n"
        f"Spreadsheet Contact Notes:\n"
        f"{row.contactNotes if row.contactNotes else None}\n\n"
        f"-------\n",
    )
