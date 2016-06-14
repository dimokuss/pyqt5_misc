import sys
import traceback

from PyQt5.QtCore import *
from dselib.baseui.services.dseservice import DseService

class ItemService(DseService):
    """
    Represents a service specifically for dealing with items.
    """
    item_naming_toggled = pyqtSignal()

    def __init__(self, context, service_id):
        """
        Initializes the ItemService instance.
        context -- The context in which the service is instantiated.
        service_id -- A string defining the id of the service.
        """
        DseService.__init__(self, context, service_id)
        self.framework_service = None
        self.lws_manager = None
        self.context = context
        self.tool_service = None

    def initialize_service(self):
        """
        Initializes the service.  This takes place after all services have been registered and all configuration items have been loaded.
        """
        self.framework_service = self.context.get_service("Framework")
        self.lws_manager = self.framework_service.lws_manager

    def toggle_display_name(self):
        """
        Toggles the display name between full and abbreviated.
        """
        show_full_name = self.lws_manager.sys_settings['show_full_name']
        if show_full_name == 'True':
            self.lws_manager.sys_settings['show_full_name'] = 'False'
        else:
            self.lws_manager.sys_settings['show_full_name'] = 'True'

        # fire the toggle signal
        self.item_naming_toggled.emit()

    def get_display_name(self, item_revision):
        """
        Serves as a central point of retrieving the display name for the given item revision.
        item_revision -- The item revision for which to get the display name for.
        """
        show_full_name = self.lws_manager.sys_settings['show_full_name']
        return item_revision.getDisplayName() if show_full_name == "True" else item_revision.getAbbreviatedDisplayName()

    def explain_display_name(self, item_revision):
        """
        Serves as a central point of retrieving the display name for the given item revision.
        item_revision -- The item revision to get an explanation for.
        """
        show_full_name = self.lws_manager.sys_settings['show_full_name']
        return item_revision.explainDisplayName()

    def get_short_name(self, item_revision):
        """
        Returns the abbreviated name of the item revision.
        item_revision -- The item revision for which to get the short name for.
        """
        return item_revision.getAbbreviatedDisplayName()

    def is_possible_to_open(self, workset):
        """
        Determines if it is possible to open items in the given workset.
        A workset can be opened if it contains no editable item revisions already open in another workset or that are in the Completed, Withdrawn, or CheckedOut by someone else state.
        workset -- The workset to determine if it's possible to open.
        returns -- a tuple of (result, offending_item_revisions) where result is True if the workset can be opened and False otherwise.
        If result is True, offending_item_revisions will be None.  If result is False, offending_item_revisions will be a list of tuples (item revision, reason) that prevent opening.
        """
        if workset is None:
            return False

        offending_item_revisions = []
        for item_revision in workset.get_editable_item_revisions():
            if is_item_opened(item_revision):
                offending_item_revisions.append((item_revision, "Already open in " + get_workset_item_is_opened_in(item_revision)))
            elif (item_revision.getCpdState() in (CpdStateEnum.Completed, CpdStateEnum.Withdrawn)) or ((item_revision.getCpdState() == CpdStateEnum.CheckedOut) and (item_revision.getOwner() != self.framework_service.aces_session.getCurrentUserName())):
                offending_item_revisions.append((item_revision, "Not in a state that can be made editable (" + str(item_revision.getCpdState()) + ")"))

        if len(offending_item_revisions) == 0:
            return (True, None)

        return (False, offending_item_revisions)

    def collect_variant_containers_with_parents(self, structure_item):
        print('should traverse', structure_item)

        # see if it has any references
        for tag_name in structure_item.getReferenceTagNames():
            if structure_item.getReferenceDefinition(tag_name).isArray():
                for _key, child in list(structure_item.getReferencesMap(tag_name).items()):
                    if child and child.getItemType() == ItemTypeEnum.Structure:
                        print('structure child', child)
                        for tmp in self.collect_variant_containers_with_parents(child):
                            yield tmp
                    elif child and child.getItemType() == ItemTypeEnum.Variant:
                        print('variant child', child)
                        yield child, None
            else:
                child = structure_item.getReference(tag_name)
                if child and child.getItemType() == ItemTypeEnum.Structure:
                    print('structure child', child)
                    for tmp in self.collect_variant_containers_with_parents(child):
                        yield tmp
                elif child and child.getItemType() == ItemTypeEnum.Variant:
                    print('variant child', child)
                    yield child, None

    def collect_item_revisions_with_parents(self, folder, recurse=True):
        """
        Collects the item revisions from the given folder.
        folder -- The folder to collect the item revisions from.
        recurse -- True to gather from the sub folders as well, False otherwise.
        returns -- A list of tuples (item_revision, parent_folder).
        """
        results = []

        self._collect_item_revisions_with_parents(folder, results, recurse)

        return results

    def _collect_item_revisions_with_parents(self, folder, results, recurse):
        """
        Collects the item revisions from the given folder and puts them in the list defined by results.
        folder -- The folder to collect the item revisions from.
        results -- The list to add the results to.
        recurse -- True to gather from the sub folders as well, False otherwise.
        returns -- A list of tuples (item_revision, parent_folder).
        """
        for item_revision in folder.contained_item_revisions:
            results.append((item_revision, folder))

        # now do the sub folders
        if isinstance(folder, WorkspaceFolder) and recurse:
            for sub_folder in folder.sub_folders:
                self._collect_item_revisions_with_parents(sub_folder, results, recurse)

    def collect_item_revisions(self, folder, recurse=True):
        """
        Collects the item revisions from the given folder.
        folder -- The folder to collect the item revisions from.
        recurse -- True to gather from the sub folders as well, False otherwise.
        returns -- A list of item revisions.
        """
        results = []

        self._collect_item_revisions(folder, results, recurse)

        return results

    def _collect_item_revisions(self, folder, results, recurse=True):
        """
        Collects the item revisions from the given folder and puts them in the list defined by results.
        folder -- The folder to collect the item revisions from.
        results -- The list to add the item revisions to.
        recurse -- True to gather from the sub folders as well, False otherwise.
        """
        # gather the item revisions in the folder itself
        results.extend(folder.contained_item_revisions)

        # now do the sub folders
        if isinstance(folder, WorkspaceFolder) and recurse:
            for sub_folder in folder.sub_folders:
                self._collect_item_revisions(sub_folder, results, recurse)

    def can_delete_item_revision(self, item_revision):
        """
        Determines if the specified item revision can be deleted from the current session.
        item_revision -- The item revision to check.
        returns -- True if the item revision can be deleted and False otherwise.
        """
        if item_revision is None:
            return False

        return (item_revision.getDefinition().getItemType() == ItemTypeEnum.Data) and (item_revision.getCpdState() == CpdStateEnum.Local)

    def delete_item_revision(self, item_revision):
        """
        Deletes the specified item revision from the current session.
        item_revision -- The item revision to delete.
        """
        if item_revision is None:
            return

        self.lws_manager.delete_item(item_revision)

    def delete_folder(self, folder, parent_folder):
        """
        Deletes the specified folder from the local workspace.
        Deleting a folder removes the links to all item revisions in that folder and deletes all sub-folders recursively.
        folder -- The folder to delete.
        parent_folder -- The parent folder of the folder being deleted.
        """
        # remove the item revision links
        for item_revision in folder.contained_item_revisions:
            folder.remove_item_revision(item_revision)

        # now do the same thing for each sub-folder
        for sub_folder in folder.sub_folders:
            if isinstance(sub_folder, Workset):
                self.delete_workset(sub_folder, folder)
            else:
                self.delete_folder(sub_folder, folder)

        # now remove the folder
        parent_folder.remove_folder(folder)

    def delete_workset(self, workset, parent_folder):
        """
        Deletes the specified workset from the local workspace.
        workset -- The workset to delete.
        parent_folder -- The parent folder of the workset being deleted.
        """
        # remove the item revision links
        for item_revision in workset.contained_item_revisions:
            workset.remove_item_revision(item_revision)

        # remove the workset
        parent_folder.remove_folder(workset)

    def create_item(self, item_type_definition, name, attributes={}, references={}, close_after=False):
        """
        Creates a new item in the local workspace of the specified type with the specified attributes and references.
        Invokes create item on the session and then immediately saves the item so it is persisted.
        item_type_definition -- The type definition of the item to create.
        name -- The base name of the new item.
        attributes -- A dictionary of {name: (metaDataEntryDefinition, value)} where name is the name of the meta data entry and value is the value to set.
        references -- A dictionary of {tag: AcesItemRevision} where tag is either a tag name or a concatenated tag#key name.
        close_after -- True to close the item after creating, False otherwise.
        returns -- The first revision of the newly created item.
        """
        new_item_revision = self.framework_service.aces_session.createItem(item_type_definition, name, attributes, references)
        self.lws_manager.save_single_item(new_item_revision, close_after)

        return new_item_revision

    def resolve_item(self, item_id, item_revision):
        """
        Resolves the given id and revision into an aces item revision.
        item_id -- The id of the item to resolve.
        item_revision -- The revision of the item to resolve.
        returns -- An AcesItemRevision representing the resolved item revision.
        """
        return self.lws_manager.load_item_revision(item_id, item_revision)

    def add_items_to_cpd(self, item_revisions, projects):
        """
        Adds the specified set of item revisions to the CPD system.
        Note that because an item revision might also have references to other Local item revisions
        those item revisions need to be added as well (recursively).  Therefore, ensure you call
        item_service.find_references(itemRevision, [], CpdStateEnum.Local, true) to obtain the full list
        of item revisions you should pass to this method.
        item_revisions -- A list of item revisions that will be added to CPD.
        projects -- A list of projects that the item revisions will be added to.
        returns -- A list of strings describing errors that occurred during the add.
        """
        errors = []
        # ensure the item revision isn't null and is in the state local
        if item_revisions is None:
            raise ValueError("Expected valid list of item revision instances!")

        for i, item_revision in enumerate(item_revisions):
            # TODO: figure out how to use the feedback service for this
            print(i + 1, '/', len(item_revisions), item_revision.getName())

            if item_revision.getCpdState() != CpdStateEnum.Local:
                raise ValueError("Only item revisions in the state \'Local\' can be added to the CPD system!")

            # add the item to CPD
            try:
                if not item_revision.isEditable():
                    self.lws_manager.open_item(item_revision)

                self.lws_manager.add_item(item_revision, projects)
                self.lws_manager.save_single_item(item_revision)
            except Exception as e:
                # TODO: this logic should go into the feedback service itself
                sys.stderr.write(''.join(
                    traceback.format_stack()[:-1] +
                    traceback.format_exception(*sys.exc_info())[1:]
                ))
                errors.append(str(e))

        # now that item revisions have been created we can check them all in to complete the add
        # this will add the meta-data, data objects, and attachments
        for item_revision in item_revisions:
            # check-in the item
            try:
                self.lws_manager.checkin_item(item_revision)
            except Exception as e:
                # TODO: this logic should go into the feedback service itself
                sys.stderr.write(''.join(
                    traceback.format_stack()[:-1] +
                    traceback.format_exception(*sys.exc_info())[1:]
                ))
                errors.append(str(e))

        return errors

    def checkout_item(self, item_revision):
        """
        Checks the item revision out of the CPD system.
        item_revision -- The item revision to check out.
        """
        self.lws_manager.checkout_item(item_revision)

    def checkin_item(self, item_revision):
        """
        Checks the item revision into the CPD system.
        item_revision -- The item revision to check in.
        """
        self.lws_manager.save_single_item(item_revision)
        self.lws_manager.checkin_item(item_revision)

    def revise_item(self, item_revision):
        """
        Revises the given item revision in the CPD system.
        item_revision -- The item revision to revise.
        returns -- The new revision of the item.
        """
        new_revision = None
        if item_revision is not None:
            if item_revision.getCpdState() != CpdStateEnum.Completed:
                raise ValueError("Only item revisions in the state \'Completed\' can be revised in the CPD system!")

            new_revision = self.lws_manager.revise_item(item_revision)

        return new_revision

    def withdraw_item(self, item_revision):
        """
        Withdraws the item revision in the CPD system.
        item_revision -- The item revision to withdraw.
        """
        self.lws_manager.withdraw_item(item_revision)

    def complete_items(self, item_revisions):
        """
        Completes the given item revisions in the CPD system.
        item_revisions -- A list of item revisions to complete.
        returns -- A list of error messages indicating errors that occurred during the process.
        """
        # ensure the item revision isn't null
        errors = []
        if item_revisions is None:
            raise ValueError("Expected valid list of item revision instances!")

        for item_revision in item_revisions:
            if (item_revision.getCpdState() != CpdStateEnum.InPreparation) or (item_revision.getOwner() != self.lws_manager.sys_settings['cpd_user']):
                raise ValueError("Only item revisions in the state \'InPreparation\' and owned by you can be completed in the CPD system!")

            try:
                self.lws_manager.complete_item(item_revision)
            except Exception as e:
                errors.append(str(e))

        return errors

    def get_indirect_references(self, item_revision, tag):
        """
        Retrieves the reference defined by tag from the base item revision.
        item_revision -- The item_revision that is the source for the references to retrieve.
        tag -- A string defining the tag path of the references to retrieve, either direct (i.e. single tag) or indirect (i.e. dot notation tag).
        returns -- A list of item revisions, of length one in the case of a non-array query containing all item revisions in an array query.
        """
        # TODO: the name of this method is wrong - it should just be get_references and the method should determine if it's direct or indirect
        tag_elements = tag.split('.')
        base_item_revision = item_revision
        refs = []
        for tag_element in tag_elements:
            if base_item_revision.getDefinition().getReferenceDefinitionByTag(tag_element).isArray():
                # note: this only works if the array reference is last in the dot notation query
                # we have no support for intermediate array queries
                for key in base_item_revision.getReferenceKeys(tag_element):
                    refs.append(base_item_revision.getReference(tag_element, key))
            else:
                base_item_revision = base_item_revision.getReference(tag_element)
                if base_item_revision is None:
                    # can't go any further in the recursion
                    return []

        # if we recursed down and got a final reference, add it to the inputs
        refs.append(base_item_revision)
        return refs

    def get_indirect_reference_definition(self, item_revision, tag):
        """
        Retrieves the reference definition defined by tag from the given item revision.
        item_revision -- The item_revision that is the source for the references to retrieve.
        tag -- A string defining the tag path of the references to retrieve, either direct (i.e. single tag) or indirect (i.e. dot notation tag).
        returns -- A reference definition for the given reference.
        """
        tag_elements = tag.split('.')
        base_item_revision = item_revision
        for i in range(0, len(tag_elements) - 1):
            base_item_revision = base_item_revision.getReference(tag_elements[i])
            if base_item_revision is None:
                break

        if base_item_revision is None:
            return None

        return base_item_revision.getReferenceDefinition(tag_elements[-1])

    def set_indirect_reference(self, source_item_revision, tag, target_item_revision):
        """
        Sets the reference defined by tag on the source item revision to the target item revision.
        source_item_revision -- The source of the reference.
        tag -- The tag defining the reference to be set.  The tag may be a direct or indirect.
        target_item_revision -- The target item revision to set as the referenced item revision.
        """
        tag_elements = tag.split('.')
        base_item_revision = source_item_revision
        for i in range(0, len(tag_elements) - 1):
            base_item_revision = base_item_revision.getReference(tag_elements[i])
            if base_item_revision is None:
                break

        if base_item_revision is None:
            raise RuntimeError("Could not set reference on null item revision!")

        base_item_revision.setReference(tag_elements[-1], target_item_revision)

    def create_task_output(self, base_item_revision, tag, parent_folder):
        """
        Creates a single task output for the given tag from the given base item revision.
        base_item_revision -- The base item revision off which to create the task outputs.
        tag -- The tag defining the output reference to create.
        parent_folder -- The parent folder to which the new output will be added to.
        """
        # get the reference definition for the output
        reference_definition = self.get_indirect_reference_definition(base_item_revision, tag)

        # create the output item
        output_item_attributes = self.derive_output_attributes(reference_definition.getItemDefinition(), base_item_revision)
        output_item_revision = self.create_item(reference_definition.getItemDefinition(), self.get_unique_item_name(reference_definition.getItemDefinition(), parent_folder), output_item_attributes, None)

        # set the reference to the output item
        self.set_indirect_reference(base_item_revision, tag, output_item_revision)

        return output_item_revision

    def create_outputs(self, tool_definition, base_item_revision, parent_folder):
        """
        Creates the output items for the given base item revision and the given tool definition in the given parent folder.
        This method assumes that all validation has been done on the tool definition with regard to indirect references (i.e. dot notation references)
        to make sure that the intermediate item revisions are editable!
        tool_definition -- The tool definition to use to find the outputs.
        base_item_revision -- The item revision off which to create the referenced outputs.
        parent_folder -- The parent folder to which the new outputs will be added to.
        """
        created_item_revisions = []

        # look up the tool definition to find out what outputs we have to create
        # the references come back as a list of tuples (tag, ToolIOReference)
        tool_references = tool_definition.get_references()
        for (tag, tool_reference) in tool_references:
            if tool_reference == ToolIOReference.Output:
                # check whether a reference is already set on the item or not
                # for Output types, the system will always create one, but we check whether this is a situation where that output
                # has been previously created (i.e. create scenario vs. launch tool scenario)
                # it may also be the case here that the reference is a dot notation reference, so we have to keep this in mind when getting the reference
                referenced_item_revisions = self.get_indirect_references(base_item_revision, tag)
                if not referenced_item_revisions:
                    # get the item reference definition so we know the type
                    reference_definition = self.get_indirect_reference_definition(base_item_revision, tag)

                    # create the output item
                    output_item_attributes = self.derive_output_attributes(reference_definition.getItemDefinition(), base_item_revision)
                    output_item_revision = self.create_item(reference_definition.getItemDefinition(), self.get_unique_item_name(reference_definition.getItemDefinition(), parent_folder), output_item_attributes, None)

                    # set the reference to the output item
                    self.set_indirect_reference(base_item_revision, tag, output_item_revision)
                    created_item_revisions.append(output_item_revision)

        return created_item_revisions

    def calculate_workset_dependencies(self, base_item_revision):
        """
        Determines what the work and supporting items should be for the given base item revision.
        base_item_revision -- The item revision to calculate the workset dependencies for.
        returns -- A 2-tuple of lists, the first for work items and the second for supporting items.
        """
        if base_item_revision is None:
            raise ValueError("Unable to calculate workset dependencies for a null base item revision!")

        work_items = []
        supporting_items = []

        # get the default tool definition for the given base item revision
        # the tool definition states the inputs, outputs, and tasks
        # the rule for placing into worksets is the following:
        # 1. an "input" reference is always a supporting item
        # 2. an "output" reference is always a work item
        # 3. a "task" reference is a work item if it's edit attribute is set to "true", otherwise it's a supporting item
        default_tool_definition = self.tool_service.get_default_tool_definition(base_item_revision.getDefinition().getName())
        io_references = default_tool_definition.get_references()
        for tag, tool_io_reference in io_references:
            refs = self.get_indirect_references(base_item_revision, tag)
            if refs:
                if (tool_io_reference == ToolIOReference.Input) or (tool_io_reference == ToolIOReference.OptionalInput):
                    supporting_items.extend(refs)
                else:
                    work_items.extend(refs)

        # all input and output items have been gathered, now we do the task items
        for task in default_tool_definition.get_tasks():
            for task_tag in task.get_tags():
                refs = self.get_indirect_references(base_item_revision, task_tag.get_tag())
                if refs:
                    if task_tag.is_editable():
                        work_items.extend(refs)
                    else:
                        supporting_items.extend(refs)

        # we have all the "direct" dependencies
        # the last thing to check is if an item appears in both, then we can remove the reference in the supporting items
        for work_item in work_items:
            if work_item in supporting_items:
                supporting_items.remove(work_item)

        return (work_items, supporting_items)

    def create_item_and_outputs(self, item_type_definition, tool_definition, parent_folder, name, attributes, references, task_references, close_after=False):
        """
        Creates an item and its corresponding outputs for the given tool.
        item_type_definition -- The item type definition to use as a basis for creating the item.
        tool_definition -- The tool definition to use to determine what the outputs to create should be.
        parent_folder -- The parent folder to which the automatically created outputs will be added.
        name -- The name of the new item.
        attributes -- The attributes to set on the new item.
        references -- The references to set on the new item.
        task_references -- The task references to set on the new item.
        close_after -- True to close the item after creating, False otherwise.
        """
        if item_type_definition is None:
            raise ValueError("Must provide a valid type definition when creating an item!")

        if tool_definition is None:
            raise ValueError("Must provide a valid tool definition when requesting output item creation!")

        if parent_folder is None:
            raise ValueError("Must provide a valid parent folder when requesting output item creation!")

        # since some tools have outputs that are indirect references, we have to ensure all item revisions in the middle
        # are in a state that they can be edited - otherwise we cannot create the required output references!
        created_item_revisions = []

        # first create the base item
        base_item_revision = self.create_item(item_type_definition, name, attributes, references)
        created_item_revisions.append(base_item_revision)

        # now create the outputs
        created_output_revisions = self.create_outputs(tool_definition, base_item_revision, parent_folder)
        created_item_revisions.extend(created_output_revisions)

        # finally, for each task the user wants to perform, we need to create those items as well
        for task in task_references:
            for tag in task_references[task]:
                if task_references[task][tag] is None:
                    # we only want to automatically create an instance of the referenced item if the reference is not an array valued reference
                    if not self._is_array_reference(base_item_revision, tag):
                        # if there is no reference set, but the task is selected, we need to create this object
                        created_item_revisions.append(self.create_task_output(base_item_revision, tag, parent_folder))
                else:
                    # they chose one, so make sure we set the reference
                    self.set_indirect_reference(base_item_revision, tag, task_references[task][tag])

        # save the new items after setting all those references
        for item_revision in created_item_revisions:
            self.lws_manager.save_single_item(item_revision, close_after)

        return created_item_revisions

    def _is_array_reference(self, item_revision, tag):
        """
        Determines whether the reference from the given item revision with the given tag is an array reference or not.
        item_revision -- The item revision off which to check the tag.
        tag -- The name of the reference to check.
        returns -- True if the definition is an array reference, False otherwise.
        """
        reference_definition = item_revision.getReferenceDefinition(tag)
        return reference_definition.isArray()

    def get_unique_item_copy_name(self, item_revision, parent_folder):
        """
        Retrieves a unique item name suitable for the given item revision in the designated parent folder.
        item_revision -- The item revision whose name will be used as a bases for a new unique name.
        parent_folder -- The folder the item will be created in to use as a search space.
        returns -- A string defining a unique name within the parent_folder space.
        """
        base_name = item_revision.getName() + "- Copy"
        name = base_name
        unique = True
        for revision in parent_folder.contained_item_revisions:
            if revision.getName() == name:
                unique = False
                break

        current_index = 1
        new_name = name
        while not unique:
            new_name = base_name + " (" + str(current_index) + ")"
            unique = True
            for revision in parent_folder.contained_item_revisions:
                if revision.getName() == new_name:
                    unique = False
                    break

            current_index += 1

        return new_name


    def get_unique_item_name(self, item_type_definition, parent_folder):
        """
        Retrieves a unique item name suitable for the item type definition in the designated parent folder.
        item_type_definition -- The type name to use as the basis for a new unique name.
        parent_folder -- The folder the item will be created in to use as a search space.
        returns -- A string defining a unique name within the parent_folder space.
        """
        base_name = item_type_definition.getDisplayName()
        name = base_name
        unique = True
        for item_revision in parent_folder.contained_item_revisions:
            if item_revision.getName() == name:
                unique = False
                break

        current_index = 1
        new_name = name
        while not unique:
            new_name = base_name + str(current_index)
            unique = True
            for item_revision in parent_folder.contained_item_revisions:
                if item_revision.getName() == new_name:
                    unique = False
                    break

            current_index += 1

        return new_name

    def get_unique_workset_name(self, parent_folder, workset_name=None):
        """
        Retrieves a unique workset name for a new workset under the parent folder.
        parent_folder -- The parent folder to use as a search space.
        workset_name -- The base name of the workset to use ("Workset" if None).
        returns -- A string defining a unique name within the parent_folder space.
        """
        name = ""
        if workset_name is not None:
            name = workset_name
        else:
            name = "Workset"

        unique = True
        for folder in parent_folder.sub_folders:
            if folder.name == name:
                unique = False
                break

        current_index = 1
        new_name = name
        while not unique:
            new_name = name + "_" + str(current_index)
            unique = True
            for folder in parent_folder.sub_folders:
                if folder.name == new_name:
                    unique = False
                    break

            current_index += 1

        return new_name

    def get_unique_folder_name(self, parent_folder, source_folder):
        """
        Retrieves a unique folder name for a new folder under the parent folder.
        parent_folder -- The parent folder to use as a search space.
        source_folder -- The source folder to use as a base name, or "New Folder" if None.
        returns -- A string representing a unique folder name within the parent_folder.
        """
        if source_folder is not None:
            name = source_folder
        else:
            name = "New Folder"
        unique = True
        for folder in parent_folder.sub_folders:
            if folder.name == name:
                unique = False
                break

        current_index = 1
        new_name = name
        while not unique:
            new_name = name + str(current_index)
            unique = True
            for folder in parent_folder.sub_folders:
                if folder.name == new_name:
                    unique = False
                    break

            current_index += 1

        return new_name

    def copy_folder(self, folder, target_folder):
        """
        Copies a source folder to the target browser item containing a folder.
        folder -- A acesframework.lws.folder.Folder instance
        target_folder -- A acesframework.lws.folder.Folder instance
        """
        # when copying a folder, we actually have to create the folder hierarchy and copy the item revisions
        # when we copy the item revisions, for now this is just a copy of the link
        new_folder_name = self.get_unique_folder_name(target_folder, folder.name)
        new_folder = target_folder.create_folder(new_folder_name)
        for item_revision in folder.contained_item_revisions:
            new_folder.add_item_revision(item_revision)

        # now do the same thing for all sub-folders
        for sub_folder in folder.sub_folders:
            if isinstance(sub_folder, Workset):
                self.copy_workset(sub_folder, new_folder)
            else:
                self.copy_folder(sub_folder, new_folder)

    def copy_workset(self, workset, target_folder):
        """
        Copies the given workset to the target folder.
        workset -- An acesframework.lws.Workset instance
        target_folder -- An acesframework.lws.Folder instance
        """
        # when copying a workset, we simply recreate the workset hierarchy and copy the item revisions over
        new_workset_name = self.get_unique_workset_name(target_folder, workset.name)
        new_workset = target_folder.create_workset(new_workset_name)

        # copy the item revisions
        for item_revision in workset.get_editable_item_revisions():
            new_workset.add_item_revision(item_revision, True)

        for item_revision in workset.get_non_editable_item_revisions():
            new_workset.add_item_revision(item_revision, False)

        # copy the BOM
        if workset.bom_item_revision is not None:
            new_workset.bom_item_revision = workset.bom_item_revision

    def copy_item_revision(self, source_item_revision, target_parent_folder):
        """
        Copies the given source item revision and returns a new item revision.
        The target_parent_folder must be a Folder instance.
        source_item_revision -- The source item revision to copy.
        target_parent_folder -- The folder where the new item revision will be copied to.
        """
        new_name = self.get_unique_item_copy_name(source_item_revision, target_parent_folder)
        copied_item_revision = self.lws_manager.copy_item(source_item_revision, new_name)

        # when an item revision is copied, the new item revision should break all links with the attribute "results"
        self.remove_results_references(copied_item_revision)

        self.lws_manager.save_single_item(copied_item_revision, True)

        return copied_item_revision

    def derive_output_attributes(self, item_type_definition, base_item_revision):
        """
        Derives and returns an attribute dictionary for the given item type definition referenced as an output of the base item revision.
        item_type_definition -- The type definition to retrieve the attributes from.
        base_item_revision -- The item revision from which to derive the attributes.
        """
        # simple rules are used to determine the attributes of a newly created output item:
        # 1. if the output item has an attribute name that matches one in the base item revision, use that attribute value
        # 2. if the output item has an attribute name that does not match one in the base item revision, ignore it (even if it's required - there's no way we can auto-determine its value)
        if (item_type_definition is None) or (base_item_revision is None):
            raise ValueError("Must provide both a valid base item revision and valid type definition for the output item!")

        attributes = {}
        output_meta_data_entries = item_type_definition.getMetaDataEntryDefinitions()
        base_item_meta_data_entries = base_item_revision.getDefinition().getMetaDataEntryDefinitions()
        for output_meta_data_entry in output_meta_data_entries:
            found_entry = None
            for base_item_meta_data_entry in base_item_meta_data_entries:
                if base_item_meta_data_entry.getName() == output_meta_data_entry.getName():
                    # found it!
                    found_entry = base_item_meta_data_entry
                    break

            # the names match, the only other thing we have to ensure is that the actual value set for the meta data entry
            # is in the list of one of the values for the output entry
            try:
                value = base_item_revision.getDelegate().getMetaData(found_entry.getName()).getValue()
                if self.verify_output_value(value, output_meta_data_entry):
                    # it's valid, we can set it
                    attributes[output_meta_data_entry.getName()] = value
            except:
                # the base item didn't have a value for the entry, so we skip it
                continue

        return attributes

    def verify_output_value(self, value, meta_data_entry_definition):
        """
        Verifies that the given value passed is valid for the given meta data entry definition.
        value -- The value to verify.
        meta_data_entry_definition -- The meta data definition to use for verification.
        returns -- True if the value is valid, False otherwise.
        """
        # we assume the value is valid if the entry has no defined enumerated values
        # if it does have enumerated values, we check whether the given value is in that list
        if len(meta_data_entry_definition.getEnumValues()) > 0:
            return value in meta_data_entry_definition.getEnumValues()

        return True

    def find_non_completed_references(self, item_revision, item_references, recurse=True):
        """
        Recursively walks the reference graph to find all references of an item revision that are in a non-completed state.
        item_revision -- The item revision to find the non-completed references for.
        item_references -- The list to add the found references to.
        recurse -- True to follow references recursively, False otherwise.
        """
        # faster to change the item revision state enum to a set of mutually exclusive flags and change find References
        # to take a set of flags ORed together, then check an AND, but this works too
        self.find_references(item_revision, item_references, CpdStateEnum.Local, True)
        self.find_references(item_revision, item_references, CpdStateEnum.CheckedOut, True)
        self.find_references(item_revision, item_references, CpdStateEnum.InPreparation, True)
        self.find_references(item_revision, item_references, CpdStateEnum.Withdrawn, True)

    # TODO: lets change the semantics so it doesn't require you pass it an empty list to fill
    def find_references(self, item_revision, item_references, state, recurse=True):
        """
        Recursively walks the reference graph to find all references of an item revision
        that have the given state.  The item_references parameter holds the list of all
        item revisions identified so far, and new item revisions should be added to the list.
        If recurse is set to False, only the direct references are returned.
        item_revision -- The item revision to find the references for.
        item_references -- The list to which the found references will be added.
        state -- The filter for references found.
        recurse -- True to follow the reference tree, False otherwise.
        """
        reference_tags = item_revision.getReferenceTagNames()
        if reference_tags is not None:
            for reference_tag in reference_tags:
                referenced_item_definition = item_revision.getReferenceDefinition(reference_tag)
                if referenced_item_definition.isArray():
                    # array-valued reference, we need to look at all the keys
                    reference_keys = item_revision.getReferenceKeys(reference_tag)
                    for reference_key in reference_keys:
                        referenced_item_revision = item_revision.getReference(reference_tag, reference_key)
                        if (referenced_item_revision is not None) and (referenced_item_revision.getCpdState() == state) and (referenced_item_revision not in item_references):
                            item_references.append(referenced_item_revision)

                            # we may now need to recurse on the referenced graph of this item
                            if recurse:
                                self.find_references(referenced_item_revision, item_references, state, recurse)
                else:
                    # single-valued reference, look at the reference itself
                    referenced_item_revision = item_revision.getReference(reference_tag)
                    if (referenced_item_revision is not None) and (referenced_item_revision.getCpdState() == state) and (referenced_item_revision not in item_references):
                        item_references.append(referenced_item_revision)

                        # we may now need to recurse on the referenced graph of this item
                        if recurse:
                            self.find_references(referenced_item_revision, item_references, state, recurse)

    def get_input_references(self, item_revision):
        """
        Retrieves the references of an item revision marked as input or optional input.
        item_revision -- The item revision to retrieve the input references for.
        returns -- A list of AcesItemRevision instances that define the input references.
        """
        inputs = []
        default_tool_definition = self.tool_service.get_default_tool_definition(item_revision.getDefinition().getName())
        if default_tool_definition is not None:
            tool_references = default_tool_definition.get_references()
            for (tag, tool_reference) in tool_references:
                if (tool_reference == ToolIOReference.Input) or (tool_reference == ToolIOReference.OptionalInput):
                    # check to see if a reference is set for this tag
                    # the tag could be in dot notation, so we may have to go down a few levels
                    tag_elements = tag.split('.')
                    base_item_revision = item_revision
                    for tag_element in tag_elements:
                        base_item_revision = base_item_revision.getReference(tag_element)
                        if base_item_revision is None:
                            # can't go any further in the recursion
                            base_item_revision = None
                            break

                    # if we recursed down and got a final reference, add it to the inputs
                    if (base_item_revision is not None) and (base_item_revision != item_revision):
                        inputs.append(base_item_revision)

        return inputs

    def get_output_references(self, item_revision):
        """
        Retrieves the references of an item revision marked as outupt or input / output.
        item_revision -- The item revision to retrieve the output references for.
        returns -- A list of AcesItemRevision instances that define the output references.
        """
        # in order to find the output reference tags, we need to consult the tool service for the item revision's default tool
        outputs = []
        default_tool_definition = self.tool_service.get_default_tool_definition(item_revision.getDefinition().getName())
        if default_tool_definition is not None:
            tool_references = default_tool_definition.get_references()
            for (tag, tool_reference) in tool_references:
                if tool_reference == ToolIOReference.Output:
                    # the tag could be in dot notation, so we may have to go down a few levels
                    tag_elements = tag.split('.')
                    base_item_revision = item_revision
                    for tag_element in tag_elements:
                        base_item_revision = base_item_revision.getReference(tag_element)
                        if base_item_revision is None:
                            # can't go any further in the recursion
                            base_item_revision = None
                            break

                    # if we recursed down and got a final reference, add it to the outputs
                    if (base_item_revision is not None) and (base_item_revision != item_revision):
                        outputs.append(base_item_revision)

        return outputs

    def remove_results_references(self, item_revision):
        """
        Removes all references from the given item revision that have a tag marked with the "results" attribute.
        item_revision -- The item revision to remove results references from.
        """
        tags = item_revision.getReferenceTagNames()
        for tag in tags:
            reference_definition = item_revision.getReferenceDefinition(tag)
            if reference_definition.getRelationType() == RelationTypeEnum.Result:
                # this is one we should be concerned with, but of course, only if the reference is set on the item revision to begin with
                if reference_definition.isArray():
                    # have to remove all of the array valued references
                    keys = item_revision.getReferenceKeys(tag)
                    for key in keys:
                        if item_revision.getReference(tag, key) is not None:
                            item_revision.removeReference(tag, key)
                else:
                    if item_revision.getReference(tag) is not None:
                        item_revision.removeReference(tag)

    def validate_reference_assignment(self, source_item, assigned_item_revision, reference_type):
        """
        Performs validation to see whether the assigned_item_revision can be assigned to the given source_item.
        If the assignment is invalid, this method will raise a ValueError.
        source_item -- The source of the reference assignment.
        assigned_item_revision -- The item revision that will be assigned as a reference.
        reference_type -- The tag that defines the reference from the source_item.
        """
        # 1. it must be of the right type
        if not self.check_reference(assigned_item_revision, reference_type):
            raise ValueError("The selected item has the wrong type or no interfaces for reference : " + reference_type)

        # 2. it must be either in the state 'Completed' or ('Local' or 'InPreparation') and owned by this user!
        # which translates to the item revision being editable
        if not source_item.isEditable():
            raise ValueError("The source item must be in a valid editable state!")

        if assigned_item_revision.getCpdState() != CpdStateEnum.Completed:
            if (assigned_item_revision.getCpdState() != CpdStateEnum.Local) and (assigned_item_revision.getCpdState() != CpdStateEnum.InPreparation) and (assigned_item_revision.getCpdState() != CpdStateEnum.CheckedOut):
                raise ValueError("The selected item must either be \'Completed\', \'Local\', or \'In Preparation\' / \'Checked Out\' and owned by you!")
            else:
                # it's either local, in prep, or checked out - we have to make sure the owner is ok
                if assigned_item_revision.getOwner() != self.lws_manager.sys_settings['cpd_user']:
                    raise ValueError("Non-Completed items must be owned by you!")

    def check_reference(self, assigned_item_revision, reference_type):
        """
        Part of the validation if the assigned_item_revision can be assigned to an item based on reference type.
        Checks to see if it is the correct type, or contains an interface to the correct type
        :param assigned_item_revision: The assigned item revision
        :param reference_type: The reference type to check against
        :return: Boolean
        """
        if assigned_item_revision.getDefinition().getName() == reference_type:
            return True

        #Check interfaces
        definition_vector = assigned_item_revision.getInterfaces()
        for dval in definition_vector:
            if dval.getName() == reference_type:
                return True

        return False


    def get_icon(self, item_revision):
        """
        Retrieves an icon for the given item revision, complete with overlay for state and consistency state.
        item_revision -- The item revision to retrieve an icon for.
        returns -- A icon that can be displayed for the item revision.
        """
        state = CpdStateEnum.Local
        consistency_state = ConsistencyStateEnum.not_checked
        if isinstance(item_revision, AcesItemRevision):
            state = item_revision.getCpdState()
            consistency_state = item_revision.getConsistencyState()
        elif isinstance(item_revision, ItemRevisionContent):
            state = item_revision.cpd_state
            consistency_state = item_revision.consistency_state

        # base image id and options
        icon_options = {}
        if item_revision.getItemType() == ItemTypeEnum.Structure:
            base_id = 'Structure'
        elif item_revision.getItemType() == ItemTypeEnum.Variant:
            base_id = 'Variant'
        else:
            base_id = "Item"

        status_overlay = {
            CpdStateEnum.Local          : None              ,
            CpdStateEnum.InPreparation  : ('overlay-orange'),
            CpdStateEnum.Checked        : ('overlay-orange'),
            CpdStateEnum.CheckedOut     : {
                True : 'overlay-green' ,
                False: 'overlay-orange',
            }[self.framework_service.aces_session.getCurrentUserName() == item_revision.getOwner()],
            CpdStateEnum.Completed      : 'overlay-blue',
            CpdStateEnum.Approved       : 'overlay-blue',
            CpdStateEnum.Released       : 'overlay-blue',
            CpdStateEnum.Withdrawn      : 'withdrawn_overlay',
            CpdStateEnum.Unknown        : None               ,
        }[state]

        # no status overlay for in-prep structure / variants until we have a concept for how to workflow them
        if item_revision.getItemType() in (ItemTypeEnum.Structure, ItemTypeEnum.Variant) and state == CpdStateEnum.InPreparation:
            status_overlay = None

        if status_overlay is not None:
            icon_options['F'] = status_overlay

        # consistency overlay
        consistency_overlay = {
            ConsistencyStateEnum.not_checked : None                   ,
            ConsistencyStateEnum.NotUpToDate : 'not_uptodate_overlay' ,
            ConsistencyStateEnum.Inconsistent: 'inconsistent_overlay' ,
            ConsistencyStateEnum.Consistent  : 'checked_out_1_overlay',
        }[consistency_state]

        if consistency_overlay is not None:
            icon_options['NW'] = consistency_overlay

        image_service = self.context.get_service("Image")

        return image_service.get_icon(base_id, **icon_options)

    def add_variant(self, variant_item, data_item, variant_name):
        """
        Adds a data item variant to the specified variant item container.
        variant_item -- The variant item on which to add the data item.
        data_item -- The data item variant to add.
        variant_name -- The name the data item variant will be referred by.
        """
        with self.lws_manager.open_context(variant_item):
            variant_item.addVariant(variant_name, data_item)
            variant_item.activate(variant_name)
        # TODO: shouldn't adding the variant be enough?
        # TODO: ... if not, should the context manager call save regardless of whether it was already opened?
        self.lws_manager.save_single_item(variant_item)
