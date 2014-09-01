# coding=utf-8
class BidValidator():
    @staticmethod
    def bid_is_valid(bid):
        """
        return true if a given bid is valid
        :param bid:
        :return: True if all the rules are respected. False instead.
        """
        required_fields = ['title', 'description', 'type']
        authorized_fields = required_fields + ['localization', 'purchaser', 'begin', 'end', 'quantity', 'category']
        errors = []
        if bid:
            for key, value in bid.items():
                if key not in authorized_fields:
                    errors.append('key %s is not valid' % key)
                elif not value:
                    errors.append('key %s could not be null' % key)

            for fields in required_fields:
                if fields not in bid:
                    errors.append('key %s is required' % fields)

            if 'begin' in bid and 'end' in bid:
                if bid['begin'] > bid['end']:
                    errors.append('Erreur')
        else:
            errors.append('bid could not be null')

        return len(errors) == 0
