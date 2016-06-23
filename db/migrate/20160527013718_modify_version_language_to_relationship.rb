class ModifyVersionLanguageToRelationship < ActiveRecord::Migration
  def change
    remove_column :versions, :language
    add_column :versions, :language_id, :integer
  end
end
