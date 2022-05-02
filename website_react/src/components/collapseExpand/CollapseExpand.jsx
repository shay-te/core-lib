const CollapseExpand = (props) => {
	const RenderChildren = () => {
        if( props.data !== {}){
            return props.data.map((item) => {
                return (
                    <div
                        className={`node-child ${props.hide ? "hide" : ""}`}
                        key={item.name}
                    >
                        {item.name}
                    </div>
                );
            });
        }
	};

	return <RenderChildren />;
};

export default CollapseExpand;
