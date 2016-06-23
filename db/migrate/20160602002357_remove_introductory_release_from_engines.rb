class RemoveIntroductoryReleaseFromEngines < ActiveRecord::Migration
  def change
    remove_column :engines, :introductory_release_id, :integer
  end
end
