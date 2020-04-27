# mkdir specification/XML-Schema_FileVersion_2/
# copy everything from specification/XML-Schema_FileVersion_1/ to specification/XML-Schema_FileVersion_2/
# rename all files in XML-Schema_FileVersion_2 to end in _2 instead of _1
# edit all individual files in specification/XML-Schema_FileVersion_2/
# - change revision number
# - change _1 to _2 throughout
# - make actual changes
# copy All file to top specification folder:
cp specification/XML-Schema_FileVersion_2/NewsML-G2_2.28-spec-All-Power_2.xsd specification/NewsML-G2_2.28-spec-All-Power.xsd
# copy latest revisions of individual files to specification/individual folder:
cp specification/XML-Schema_FileVersion_2/NewsML-G2_2.28-spec-ConceptItem-Power_2.xsd specification/individual/NewsML-G2_2.28-spec-ConceptItem-Power.xsd
cp specification/XML-Schema_FileVersion_2/NewsML-G2_2.28-spec-KnowledgeItem-Power_2.xsd specification/individual/NewsML-G2_2.28-spec-KnowledgeItem-Power.xsd 
cp specification/XML-Schema_FileVersion_2/NewsML-G2_2.28-spec-NewsItem-Power_2.xsd specification/individual/NewsML-G2_2.28-spec-NewsItem-Power.xsd 
cp specification/XML-Schema_FileVersion_2/NewsML-G2_2.28-spec-NewsMessage-Power_2.xsd specification/individual/NewsML-G2_2.28-spec-NewsMessage-Power.xsd 
cp specification/XML-Schema_FileVersion_2/NewsML-G2_2.28-spec-PackageItem-Power_2.xsd specification/individual/NewsML-G2_2.28-spec-PackageItem-Power.xsd 
cp specification/XML-Schema_FileVersion_2/NewsML-G2_2.28-spec-PlanningItem-Power_2.xsd specification/individual/NewsML-G2_2.28-spec-PlanningItem-Power.xsd 
cp specification/XML-Schema_FileVersion_2/NewsML-G2_2.28-spec-Framework-Power_2.xsd specification/individual/NewsML-G2_2.28-spec-Framework-Power.xsd
# edit the specification/individual files to remove _<revision> references...
# TODO implement this with some sed magic
# check that they're all done - this should return nothing:
grep '_2.xsd' specification/individual/*.xsd
# generate xml schema docs using xml spy

