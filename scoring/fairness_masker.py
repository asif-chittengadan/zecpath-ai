import copy


class FairnessMasker:

    def mask(self, resume):

        masked = copy.deepcopy(resume)

        if "Others" in masked:

            masked["Others"] = []

        if "personal_details" in masked:

            masked["personal_details"] = {}

        if "contact" in masked:

            masked["contact"] = {}

        return masked