#!/bin/zsh

# load shared env vars
echo "Loading shared environment variables including new NewsML-G2 version number"
. release-tools/newsmlg2-config-vars.sh

# create local vars
POWER_XSD="$COMBINED_XSD_NO_REVISION"

EXAMPLE_DIR="examples"

# "LISTING_24_News_Message_conveying_a_complete_News_Package.xml" \
# We don't include the NITF XSD so this fails \
# "LISTING_25_An_NITF_marked-up_article_conveyed_in_inlineXML.xml" \
# fragments
# "LISTING_7_Group_Set_example_showing_Hierarchical_Package_Structure.xml" \
# "LISTING_8_Group_Set_example_showing_an_ALT_Package_Mode.xml" \
# "LISTING_9_Group_Set_example_showing_a_SEQ_Package_Mode.xml" \
# "LISTING_28_Illustrating_Located_Subject_and_Dateline.xml" \

echo "Testing example files against the new schema (note that we leave out some samples that do not validate properly)"
for exfile in \
    "LISTING_1_A_NewsML-G2_News_Item.xml" \
    "LISTING_2_NewsML-G2_Text_Document.xml" \
    "LISTING_3A_Photo_in_NewsML-G2_(URI_sibling_attributes).xml" \
    "LISTING_3_Photo_in_NewsML-G2.xml" \
    "LISTING_4_Multiple_Renditions_of_a_Video_in_NewsML-G2.xml" \
    "LISTING_5_Multi-part_Video_in_NewsML-G2.xml" \
    "LISTING_6_Simple_NewsML-G2_Package.xml" \
    "LISTING_10_Abstract_Concept_conveyed_in_a_NewsML-G2_Concept_Item.xml" \
    "LISTING_11_Person_Concept_conveyed_in_a_NewsML-G2_Concept_Item.xml" \
    "LISTING_12_Knowledge_Item_for_Access_Codes.xml" \
    "LISTING_13_Complete_Catalog_Item.xml" \
    "LISTING_14_Event_sent_as_a_Concept_Item.xml" \
    "LISTING_15_Two_Related_Events_in_a_Knowledge_Item.xml" \
    "LISTING_16_A_Set_of_Events_carried_in_a_News_Item.xml" \
    "LISTING_17_Planning_Item_a_CCL.xml" \
    "LISTING_18_Planning_Item_at_PCL.xml" \
    "LISTING_19_Planning_Item_with_delivery_at_CCL.xml" \
    "LISTING_20_Planning_Item_with_delivery_at_PCL.xml" \
    "LISTING_21_A_complete_sample_SportsML-G2_document.xml" \
    "LISTING_22_Sports_story_in_NewsML-G2NITF.xml" \
    "LISTING_23_SportsML-G2_Package.xml" \
    "LISTING_26_Embedded_photo_metadata_fields_mapped_to_NewsML-G2.xml" \
    "LISTING_27_Company_Financial_Information.xml" \
    "LISTING_29_Hop_History.xml" \
    "Receiver View.xml";
do
    xmllint --noout --schema $POWER_XSD $EXAMPLE_DIR/$exfile;
done

echo "Done."
