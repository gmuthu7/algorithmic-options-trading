from tab.tab_model import TabModel


class TabService:
    def add_tab(self, tab: TabModel):
        tab.pk = tab.id
        tab.save()

    def get_tabs(self):
        # get all contexts
        tabs = [self.get_tab(id) for id in TabModel.all_pks()]
        return tabs

    def get_tab(self, id: str):
        # get a specific context
        return TabModel.get(id)

    def delete_tab(self, id: str):
        # get a specific context
        return TabModel.delete(id)
